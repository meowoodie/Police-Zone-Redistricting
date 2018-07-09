# R code for applying regression analysis between census data and police workload.
# L1 penalty will be applied onto census features in order to select the most 
# important factors that have principal impact on the change of workload. 
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

library(dplyr)
library(tidyr) 
root.dir      = 'Desktop/workspace/Atlanta-Zoning'
data.dir      = paste(root.dir, 'data/census', sep='/')
map.path      = 'Desktop/workspace/Atlanta-Zoning/data/cross_map.csv'
workload.path = 'Desktop/workspace/Atlanta-Zoning/data/workload_by_beat.csv'
source(paste(root.dir, 'scripts/preproc.R', sep='/'))

# Step 1.
# Read data from local files. The dataset is organized hierarchically by the 
# categories of census feature and years. The following code would traverse 
# through the hierarchy of files and read the data into dataframes.
# - Census data for population 
population.df = read.census(
  data.dir, 
  'population, age and sex, race and ethnicity', 
  c('Estimate; SEX AND AGE - Total population', 
    'Estimate; SEX AND AGE - 20 to 24 years', 
    'Estimate; SEX AND AGE - 25 to 34 years'))

# - Census data for Education
education.df = read.census(
  data.dir, 
  'Educational Attainment', 
  c('Total; Estimate; Less than high school graduate', 
    'Total; Estimate; High school graduate (includes equivalency)', 
    "Total; Estimate; Some college or associate's degree",
    "Total; Estimate; Bachelor's degree or higher"))

# - Census data for Household income in the past 12 months
employment.df = read.census(
  data.dir, 
  'Employment Status', 
  c('Total; Estimate; Population 16 years and over'))

# - Workload by beat
workload        = read.csv(workload.path, header=FALSE, sep = ',', stringsAsFactors=FALSE)
names(workload) = as.matrix(workload[1, ])
workload        = workload[-1, ]

# Step 2.
# Merge all the census data into a dataframe, and convert the data in
# the table from zipcode to beat.
df.list           = list(population.df, education.df, employment.df)
census.zipcode.df = merge.census(df.list)
census.beat.df    = zip2beat(map.path, census.zipcode.df)




