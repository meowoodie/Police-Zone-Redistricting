# R code for applying regression analysis between census data and police workload.
# L1 penalty will be applied onto census features in order to select the most 
# important factors that have principal impact on the change of workload. 
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

library(dplyr)
library(tidyr)
library(glmnet)
library(stringr)
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
source(paste(root.dir, 'scripts/preproc.R', sep='/'))

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
# Merge all the census data into a dataframe, and convert the data in
# the table from zipcode to beat.
df.list           = list(population.df, education.df, employment.df)
census.zipcode.df = merge.mdf(df.list)
census.beat.df    = zip2beat(map.path, census.zipcode.df)
colnames(census.beat.df)[10] = 'beat' # change col name from 'Id2' to 'beat'

# Step 3.
# Linear regression & LASSO
train.df = merge.mdf(list(census.beat.df, workload.df), keys=c('beat', 'year'))
train.df = train.df[complete.cases(train.df), ]

lr = lm(train.df[, 11] ~ train.df[, 3:10])
# lasso = glmnet(train.df[,factors], train.df['workload'], alpha = 1)


