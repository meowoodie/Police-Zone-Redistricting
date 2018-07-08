# R code for applying regression analysis between census data and police workload.
# L1 penalty will be applied onto census features in order to select the most 
# important factors that have principal impact on the change of workload. 
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

root.dir   = "Desktop/workspace/Atlanta-Zoning"
data.dir   = paste(root.dir, "data/census", sep="/")
source(paste(root.dir, "scripts/preproc.R", sep="/"))

# Step 1.
# Read data from local files. The dataset is organized hierarchically by the 
# categories of census feature and years. The following code would traverse 
# through the hierarchy of files and read the data into dataframes.
# - Census data for population 
population.df = read.census(
  data.dir, 
  "population, age and sex, race and ethnicity", 
  c("Estimate; SEX AND AGE - Total population", "Estimate; SEX AND AGE - 20 to 24 years", "Estimate; SEX AND AGE - 25 to 34 years"))

# - Census data for Education
population.df = read.census(
  data.dir, 
  "population, age and sex, race and ethnicity", 
  c("Estimate; SEX AND AGE - Total population", "Estimate; SEX AND AGE - 20 to 24 years", "Estimate; SEX AND AGE - 25 to 34 years"))



