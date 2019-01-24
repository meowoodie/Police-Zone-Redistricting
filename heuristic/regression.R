# R code for applying regression analysis between census data and police workload.
# L1 penalty will be applied onto census features in order to select the most 
# important factors that have principal impact on the change of workload. 
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

# Configurations
library(dplyr)
library(tidyr)
library(glmnet)
library(stringr)
library(plotmo)
root.dir      = 'Desktop/workspace/Zoning-Analysis'
data.dir      = paste(root.dir, 'data/census', sep='/')
map.path      = paste(root.dir, 'data/cross_map.csv', sep='/')
workload.path = paste(root.dir, 'data/workload.csv', sep='/')
population.factors = c('Estimate; SEX AND AGE - Total population', 
                       'Estimate; SEX AND AGE - 20 to 24 years', 
                       'Estimate; SEX AND AGE - 25 to 34 years')
education.factors  = c('Total; Estimate; Less than high school graduate',
                       'Total; Estimate; High school graduate (includes equivalency)',
                       "Total; Estimate; Some college or associate's degree",
                       "Total; Estimate; Bachelor's degree or higher")
employment.factors = c('Total; Estimate; Population 16 years and over')
factors = c(population.factors, education.factors, employment.factors)
source(paste(root.dir, 'heuristic/lib/preproc.R', sep='/'))
source(paste(root.dir, 'heuristic/lib/timeseries.R', sep='/'))

# TODO: Given the key name at first. Use 'Id' uniformly for all the process.
# TODO: Scaling train and predict data together at the begining

# Step 1.
# Read data from local files. The dataset is organized hierarchically by the 
# categories of census feature and years. The following code would traverse 
# through the hierarchy of files and read the data into dataframes.
# - Census data for population
population.df = read.census(
  data.dir, 
  'population, age and sex, race and ethnicity', 
  population.factors)
# - Census data for Education
education.df = read.census(
  data.dir, 
  'Educational Attainment', 
  education.factors)
# Patch:
# Predict 15 and 16 education.df because of missing data in these two years.
pred.education.df = ar.census(education.df, education.factors, ar.p=1, ar.n.ahead=2)
education.df = rbind(education.df, pred.education.df)
# - Census data for Household income in the past 12 months
employment.df = read.census(
  data.dir, 
  'Employment Status', 
  employment.factors)
# - Workload by beat
workload.df = read.workload(workload.path)

# Step 2.
# Merge all the census data into a dataframe, convert the data in
# the table from zipcode to beat, and scale the dataframe in the end.
df.list            = list(population.df, education.df, employment.df)
census.zipcode.df  = merge.mdf(df.list)
census.beat.df     = zip2beat(map.path, census.zipcode.df)
census.beat.df     = as.data.frame(census.beat.df[complete.cases(census.beat.df), ])

# Step 3.
# Fit in Linear regression & LASSO and predict future workloads
# - merge response variable and predictor variables
train.df     = merge.mdf(list(census.beat.df, workload.df), keys=c('Id2', 'year'))
# - remove rows contains NA values and scaling
train.df     = train.df[complete.cases(train.df), ]
std.train.df = train.df # scale.df(train.df, keys=c(factors, 'last workload', 'current year')) # workload is not scaled
# - fit in lm
x = as.matrix(std.train.df[c(factors, 'last workload', 'current year')])
y = as.matrix(std.train.df['workload'])
lr = lm(y ~ x)

# Step 4.
# Predict workload
# - Apply time series model to the census dataframe, and include the 
#   predicted future census data into the train.df.
n.ahead             = 3
start.year          = max(as.numeric(unique(census.beat.df$year))) + 1
pred.years          = as.character((start.year):(start.year+n.ahead-1))
pred.census.beat.df = ar.census(census.beat.df, factors, ar.p=1, ar.n.ahead=n.ahead)
pred.workload.df    = workload.df[workload.df$year==as.character(start.year-1), c('Id2', 'year', 'workload')]
# - prediction loop
for (pred.year in pred.years) {
  last.year          = as.character(as.numeric(pred.year) - 1)
  new.census.beat.df = pred.census.beat.df[pred.census.beat.df$year==pred.year, ]
  new.train.df       = new.census.beat.df
  new.train.df$`last workload` = NA # add new column 'last workload' for new.train.df
  new.train.df$`current year`  = NA # add new column 'current year' for new.train.df
  # get last workload iteratively
  for (i in 1:nrow(new.train.df)) {
    beat = new.train.df[i, 'Id2']
    # because current year is all the same value, it was supposed to be 0 after scaling.
    new.train.df[i, 'current year']  = 0 # as.numeric(new.train.df[i, 'year'])
    new.train.df[i, 'last workload'] = pred.workload.df[
      pred.workload.df$Id2==beat & pred.workload.df$year==last.year, 
      'workload']
  }
  # organize new data x
  new.std.train.df = new.train.df # scale.df(new.train.df, keys=c(factors, 'last workload'))
  new.x            = data.frame(x=I(as.matrix(new.std.train.df[c(factors, 'last workload', 'current year')])))
  # predict by std.pred.census.beat.df
  new.workload     = as.vector(predict(lr, new.x))
  # merge (beat, year) into a dataframe
  beat.col = data.matrix(new.std.train.df['Id2'])
  year.col = data.matrix(new.std.train.df['year'])
  new.workload.df  = data.frame(matrix(
    c(beat.col, year.col, new.workload),
    nrow=length(new.workload)))
  colnames(new.workload.df) = c('Id2', 'year', 'workload')
  pred.workload.df = rbind(pred.workload.df, new.workload.df)
}

# # patch
# pred.workload.df = pred.workload.df[!(pred.workload.df$Id2%in%c("701", "705", "704","703","706","101","702","709")), ]

# Write results
write.csv(census.beat.df, file = "census_beat.csv")
write.csv(pred.census.beat.df, file = "pred_census_beat.csv")
write.csv(pred.workload.df, file = "pred_workload.csv")