# R code for applying regression analysis between census data and police workload.
# L1 penalty will be applied onto census features in order to select the most 
# important factors that have principal impact on the change of workload. 
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

root.dir   = "Desktop/workspace/Atlanta-Zoning"
data.dir   = paste(root.dir, "data/census", sep="/")
# categories = c("Educational Attainment", "Employment Status", "Marital Status", "population, age and sex, race and ethnicity", "School Enrollment", 
#                "income/EARNINGS IN THE PAST 12 MONTHS (INFLATION-ADJUSTED DOLLARS)")
source(paste(root.dir, "scripts/preproc.R", sep="/"))

# Step 1.
# Read data from local files. The dataset is organized hierarchically by the 
# categories of census feature and years. The following code would traverse 
# through the hierarchy of files and read the data into dataframes.
read.census(data.dir, "Educational Attainment")

# census.education.rawdata = read.csv(census.education.2011, header = FALSE, sep = ",")
# 
# names(dat) <- as.matrix(census.education.rawdata[1, ])
# dat <- dat[-1, ]
