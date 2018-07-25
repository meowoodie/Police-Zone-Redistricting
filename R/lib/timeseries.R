# R functions for forecasting the future census data based on historical 
# census data by applying time series model
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

# Function for forecasting the future census (indicated factors) data by 
# applying Auto Regressive Model. (factors and areas are mutually independent)
# Params:
# - census.df: the dataframe contains all the information, including factors,
#              key for areas, key for time, and p for AR.
# - factors:   fit AR model independently regarding each of factors in each 
#              of areas in the dataframe. 
# - ar.p:      p value for the AR model.
# - n.ahead:   the number of values in the future that the model is going to 
#              predict.
ar.census = function (census.df, factors, ar.p=1, ar.n.ahead=3) {
  start.year     = max(as.numeric(unique(census.df$year))) + 1
  preds.year     = as.character((start.year):(start.year+ar.n.ahead-1))
  ids            = unique(census.df$Id2)
  preds.df       = data.frame()
  for (id in ids) {
    df.list = list()
    for (factor in factors) {
      # init prediction
      pred = rep(0, length(preds.year))
      # get rows with (id, factor) from census.df
      data = as.vector(census.df[census.df$Id2==id, factor])
      # fit rows in ar model and forecast the future
      result = tryCatch({
        fit  = ar(data, FALSE, ar.p)
        pred = predict(fit, n.ahead=ar.n.ahead)
        pred = as.vector(pred$pred)
      }, error=function (cond) {
        message('AR prediction failed.')
        message(paste(c(cond, '\n'), collapse=''))
        
      }, warning=function(cond) {
        message('A warning occurred.')
        message(paste(c(cond, '\n'), collapse=''))
      })
      # convert the prediction into dataframe
      pred.df = data.frame(matrix(
        c(rep(id, length(preds.year)), preds.year, pred),
        nrow=length(preds.year)))
      colnames(pred.df) = c('Id2', 'year', factor)
      # append pred.df to df.list
      df.list = c(list(pred.df), df.list)
    }
    preds.df = rbind(merge.mdf(df.list, keys=c('Id2', 'year')), preds.df)
  }
  # change data type from factor to numeric and characters
  preds.df[c('year', 'Id2')] = sapply(preds.df[c('year', 'Id2')], as.character)
  preds.df[factors] = sapply(preds.df[factors], as.character)
  preds.df[factors] = sapply(preds.df[factors], as.numeric)
  return(preds.df)
}