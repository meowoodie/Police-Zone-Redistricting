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
# - t_key:     the key stands for the time index.
# - s_key:     the key stands for the space (area). 
# - p:         p value for the AR model.
# - n.ahead:   the number of values in the future that the model is going to 
#              predict.
ar.census = function (census.df, factors, ar.p=2, ar.n.ahead=3) {
  # get X from census.df
  census.df      = census.df[order(census.df$year), ]
  time.series.df = census.df[census.df$beat=='110', factors]
  preds          = lapply(time.series.df, function (factor) {
    fit  = ar(factor, p=ar.p)
    pred = predict(fit, n.ahead=ar.n.ahead)
    return(pred)
  })
  # fit    = ar(c(26661.711, 26279.397, 25963.901, 25100.719), p=1) # X is a time series in r
  # future = predict(fit, n.ahead=1)
  
}