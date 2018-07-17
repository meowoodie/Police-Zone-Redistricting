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
  # remove rows with NA value
  census.data = census.data[complete.cases(census.data), ]
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

# Function for scaling (mean-centering) the indicated columns in the data frame
# Param:
# - df:   a dataframe for scaling
# - keys: the key names for the columns which needs to be mean-centered.
scale.df = function (df, keys) {
  new.sub.df = scale(df[, keys], scale=TRUE, center=TRUE)
  new.df     = merge(df[, !(names(df) %in% keys)], new.sub.df, by='row.names', sort=FALSE)
  new.df     = new.df[, !colnames(new.df) %in% c('Row.names')]
  return(new.df)
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
  years          = unique(census.zipcode.df['year'])$year
  beats          = colnames(cross.map)
  census.beat.df = data.frame()
  for (beat in beats) {
    for (year in years) {
      if (!is.na(beat)) {
        zipcode.table = cross.table[cross.table$beat==beat, ]
        for (i in 1:nrow(zipcode.table)) {
          zip = zipcode.table[i, 'zipcode']
          pct = zipcode.table[i, 'percentage']
          # check if the entry (year, zip) exists in census.zipcode.df
          if (nrow(census.zipcode.df[
            census.zipcode.df$Id2==as.character(zip) & 
            census.zipcode.df$year==as.character(year), ]) > 0) {
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
  }
  # group by (year, beat) and sum up other factors
  census.beat.df = census.beat.df %>% group_by(.dots=c('year', 'Id2')) %>% summarise_all(funs(mean))
  # # reset the index of rows
  # rownames(census.beat.df) = seq(length=nrow(census.beat.df)) 
  return(census.beat.df)
}

# Function for reading and preparing workload dataframe.
read.workload = function (workload.path) {
  workload      = read.csv(workload.path, sep = ',', stringsAsFactors=FALSE)
  workload$year = sapply(workload$year, function (year) { return(year %% 100) })
  # assign last workload for each (beat, year)
  workload$`last workload` = workload$workload
  for (i in 1:nrow(workload)) {
    cur.beat  = workload[i, 'beat']
    cur.year  = workload[i, 'year']
    last.year = as.character(as.numeric(cur.year) - 1)
    years     = unique(workload[workload$beat==cur.beat, 'year'])
    if (last.year %in% years) {
      workload[i, 'last workload'] = workload[
        workload$beat==cur.beat & workload$year==last.year, 
        'workload']
    }
    else {
      workload[i, 'last workload'] = NA
    }
  }
  # remove na values
  workload = workload[complete.cases(workload), ]
  # convert beat and year from factor to character &
  # convert workload from integer to numeric
  workload[c('beat', 'year')] = sapply(workload[c('beat', 'year')], as.character)
  workload['workload']        = sapply(workload['workload'], as.numeric)
  workload['last workload']   = sapply(workload['last workload'], as.numeric)
  return(workload)
}