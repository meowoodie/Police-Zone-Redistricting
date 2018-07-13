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
  beats          = unique(census.df$beat)
  preds.df       = data.frame()
  for (beat in beats) {
    df.list = list()
    for (factor in factors) {
      # get rows with (beat, factor) from census.df
      data    = as.vector(census.df[census.df$beat==beat, factor])
      # fit rows in ar model and forecast the future
      fit     = ar(data, FALSE, ar.p)
      pred    = predict(fit, n.ahead=ar.n.ahead)
      pred    = as.vector(pred$pred)
      # convert the prediction into dataframe
      pred.df = data.frame(matrix(
        c(rep(beat, length(preds.year)), preds.year, pred),
        nrow=length(preds.year)))
      colnames(pred.df) = c('beat', 'year', factor)
      # append pred.df to df.list
      df.list = c(list(pred.df), df.list)
    }
    preds.df = rbind(merge.mdf(df.list, keys=c('beat', 'year')), preds.df)
  }
  # change data type from factor to numeric and characters
  preds.df[c('year', 'beat')] = sapply(preds.df[c('year', 'beat')], as.character)
  preds.df[factors] = sapply(preds.df[factors], as.character)
  preds.df[factors] = sapply(preds.df[factors], as.numeric)
  return(preds.df)
}