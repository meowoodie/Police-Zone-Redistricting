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
root.dir      = 'Desktop/workspace/Atlanta-Zoning'
data.dir      = paste(root.dir, 'data/census', sep='/')
map.path      = 'Desktop/workspace/Atlanta-Zoning/data/cross_map.csv'
workload.path = 'Desktop/workspace/Atlanta-Zoning/data/workload_by_beat.csv'
population.factors = c('Estimate; SEX AND AGE - Total population', 
                       'Estimate; SEX AND AGE - 20 to 24 years', 
                       'Estimate; SEX AND AGE - 25 to 34 years')
education.factors  = c('Total; Estimate; Less than high school graduate', 
                       'Total; Estimate; High school graduate (includes equivalency)', 
                       "Total; Estimate; Some college or associate's degree",
                       "Total; Estimate; Bachelor's degree or higher")
employment.factors = c('Total; Estimate; Population 16 years and over')
factors = c(population.factors, education.factors, employment.factors)
source(paste(root.dir, 'R/preproc.R', sep='/'))

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
census.beat.df     = census.beat.df[complete.cases(census.beat.df), ]
std.census.beat.df = scale.df(census.beat.df, keys=factors)
colnames(std.census.beat.df)[2] = 'beat' # change col name from 'Id2' to 'beat'

# # - merge response variable and predictor variables
# train.df = merge.mdf(list(census.beat.df, workload.df), keys=c('beat', 'year'))
# # - remove rows contains NA values
# train.df = train.df[complete.cases(train.df), ]
# # - standardize the training data
# std.train.df = scale.df(train.df, keys=factors) 

# Step 3.
# Apply time series model to the census dataframe, and include the 
# predicted future census data into the train.df.

# Step 4.
# Linear regression & LASSO
# - apply linear regression and lasso
x  = as.matrix(train.df[factors])
y  = as.matrix(train.df['workload'])
lr = lm(y ~ x)
cv.fit = cv.glmnet(x, y, alpha=1)

# Step 5.
# plot linear regression result
mod           = glmnet(x, y)
glmcoef       = coef(mod, cv.fit$lambda.min)
coef.increase = dimnames(glmcoef[glmcoef[,1]>0,0])[[1]]
coef.decrease = dimnames(glmcoef[glmcoef[,1]<0,0])[[1]]
# get ordered list of variables as they appear at smallest lambda
allnames = names(coef(mod)[ ,ncol(coef(mod))][order(coef(mod)[ ,ncol(coef(mod))], decreasing=TRUE)])
# remove intercept
allnames = setdiff(allnames, allnames[grep("Intercept",allnames)])
# assign colors
cols = rep("gray", length(allnames))
cols[allnames %in% coef.increase] = "red"      # higher mpg is good
cols[allnames %in% coef.decrease] = "blue"     # lower mpg is not
plot_glmnet(cv.fit$glmnet.fit, label=TRUE, s=cv.fit$lambda.min, col=cols)
# plot(cv.fit)
