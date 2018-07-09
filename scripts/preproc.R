# R functions for preprocessing census dataset collected from US Census Website.
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

# Function for reading census data given specific category and factors over all 
# the recentyears (all the data files under the category), this function will 
# return a single dataframe which contains indicated factors of this category.
# Params:
# - root.dir:    root path of the input data.
# - category:    the category of census data, e.g 'Educational Attainment'.
# - factors:     the names of columns in data table.
# - numYearFlag: if true then use numeric year.
# - scaleFlag:   if true then scale the values of each factor.
read.census = function (root.dir, category, factors, numYearFlag=TRUE, scaleFlag=TRUE) {
  census.data = data.frame()
  census.path = paste(c(root.dir, category), collapse = '/')
  for (year in dir(census.path)) {
    if (!grepl('metadata', year)) {
      year.census.path = paste(c(census.path, year), collapse = '/')
      for (file in dir(year.census.path)) {
        if (grepl('with_ann.csv', file)){
          result = tryCatch({
            file.year.census.path = paste(c(year.census.path, file), collapse = '/')
            rawdata           = read.csv(file.year.census.path, header = FALSE, sep = ',', stringsAsFactors=FALSE)
            names(rawdata)    = as.matrix(rawdata[2, ])            # set second row as the names of the dataframe
            rawdata           = rawdata[-(1:3), c('Id2', factors)] # remove the metadata of the dataframe, and get indicated factors
            if (numYearFlag) { year = strsplit(year, '_')[[1]][2] }
            rawdata['year']   = rep(year, nrow(rawdata))           # add new column (year)
            rownames(rawdata) = seq(length=nrow(rawdata))          # reset the index of rows
            census.data       = rbind(census.data, rawdata)        # append current rawdata to the output (census.data)
          }, error=function (cond) {
            message(sprintf('An exception occurred.\ncategory [%s] year [%s] has been skipped.', category, year))
            message(paste(c(cond, '\n'), collapse=''))
          }, warning=function(cond) {
            message('A warning occurred.')
            message(paste(c(cond, '\n'), collapse=''))
          })
          break
        }
      }
    }
  }
  # convert character to numeric type
  census.data[factors] = sapply(census.data[factors], as.numeric)
  return(census.data)
}

# Function for merging dataframes with different factors by indicated keys. 
# The remaining (after merging) rows in the dataframe would be the minimal subset
# of all the rows appeared at least once in their original dataframes.
# Params:
# - df.list: a list of dataframes
# - keys:    an array of keys used as primary key in the merging operations.
merge.mdf = function (df.list, keys=c('Id2', 'year')) {
  # merge multiple data frames into one
  merged.df = Reduce(function(dtf1, dtf2) merge(dtf1, dtf2, keys=keys), df.list)
  return(merged.df)
}

# Function for converting census data by zipcode to census data by beat areas.
# It will calculate the percentage of the zipcode composition for each of beats,
# and add each portion of census data of zipcodes up. 
# Params:
# - map.path:  The path of the zip2beat (or cross map) table.
# - census.df: The dataframe of census data, organized by multiple key (beat, year).
zip2beat = function (map.path, census.zipcode.df) {
  # read cross.map into dataframe, row name is zipcode, col name is beat
  cross.map = read.csv(map.path, header = FALSE, sep = ',', stringsAsFactors=FALSE)
  names(cross.map)    = as.matrix(cross.map[1, ])
  rownames(cross.map) = as.matrix(cross.map[, 1])
  cross.map           = cross.map[-1, -1]
  # normalization of cross.map, make the values in each column can be added up to 1
  for (col in 1:ncol(cross.map)) {
    if (sum(cross.map[,col] != 0) != 0){
      cross.map[,col] = cross.map[,col] / sum(cross.map[,col])
    }
  }
  # generate cross.table with columns (zipcode, year, nonzero percentage)
  cross.table = data.frame()
  # names(cross.table) = c('zipcode', 'beat', 'percentage')
  for (beat in colnames(cross.map)) {
    for (zipcode in rownames(cross.map)) {
      if (!is.na(beat) & !is.null(cross.map[zipcode, beat]) ) {
        if (cross.map[zipcode, beat] > 0) {
          cross.table = rbind(cross.table, data.frame(
            'zipcode'=zipcode, 
            'beat'=beat, 
            'percentage'=cross.map[zipcode, beat]))
        }
      }
    }
  }
  # creat census.beat.df with columns names (beat)
  census.beat.df           = data.frame(matrix(ncol=ncol(census.zipcode.df), nrow=0)) # creat an empty dataframe
  colnames(census.beat.df) = colnames(census.zipcode.df)                              # assign columns names to the dataframe
  for (beat in colnames(cross.map)) {
    for (year in unique(census.zipcode.df['year'])) {
      if (!is.na(beat)) {
        zipcode.table = cross.table[cross.table$beat==beat, ]
        for (i in nrow(zipcode.table)) {
          zip = zipcode.table[i, 'zipcode']
          pct = zipcode.table[i, 'percentage']
          new.df = pct * census.zipcode.df[
            census.zipcode.df$Id2==as.character(zip) & census.zipcode.df$year==as.character(year), 
            !(names(census.zipcode.df) %in% c('Id2', 'year'))]
          new.df$year    = year
          new.df$Id2     = beat
          census.beat.df = rbind(census.beat.df, new.df)
        }
      }
    }
  }
  rownames(census.beat.df) = seq(length=nrow(census.beat.df)) # reset the index of rows
  return(census.beat.df)
}

# Function for reading and preparing workload dataframe.
read.workload = function (workload.path) {
  workload           = read.csv(workload.path, header=FALSE, sep = ',', stringsAsFactors=FALSE)
  names(workload)    = as.matrix(workload[1, ])
  rownames(workload) = as.matrix(workload[, 1])
  workload           = workload[-1, -1]
  # generate workload.table with columns (beat, year, workload)
  workload.table = data.frame()
  for (year in colnames(workload)) {
    for (beat in rownames(workload)) {
      workload.table = rbind(workload.table, data.frame(
        'beat'=beat, 
        'year'=year, 
        'workload'=workload[beat, year]))
    }
  }
  # convert beat and year from factor to character & 
  # convert workload from integer to numeric
  workload.table[c('beat', 'year')] = sapply(workload.table[c('beat', 'year')], as.character)
  workload.table['workload'] = sapply(workload.table['workload'], as.numeric)
  return(workload.table)
}