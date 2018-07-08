# R functions for preprocessing census dataset collected from US Census Website.
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

# Function for reading census data given specific category and factors over all 
# the recentyears (all the data files under the category), this function will 
# return a single dataframe which contains indicated factors of this category.
read.census = function (root.dir, category, factors) {
  census.path = paste(c(root.dir, category), collapse = '/')
  for (year in dir(census.path)) {
    if (!grepl("metadata", year)) {
      year.census.path = paste(c(census.path, year), collapse = '/')
      for (file in dir(year.census.path)) {
        if (grepl("with_ann.csv", file)){
          file.year.census.path = paste(c(year.census.path, file), collapse = '/')
          rawdata        = read.csv(file.year.census.path, header = FALSE, sep = ",")
          names(rawdata) = as.matrix(rawdata[2, ]) # set second row as the names of the dataframe
          rawdata        = rawdata[-2, ]           # remove the metadata of the dataframe
          break
        }
      }
    }
  }
}