# 
readCensusData = function (root.dir, category) {
  censusPath = paste(c(root.dir, category, "/"), collapse = '')
  years      = dir(census.path)
  for (year in years) {
    if (!grepl("metadata", year)) {
      
    }
  }
}