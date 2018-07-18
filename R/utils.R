# R functions of utilities
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

# Function for plotting the result of variable selection by glmnet.
# note: 
# cv.fit = cv.glmnet(x, y, alpha=1)
# mod    = glmnet(x, y)
plot.cv.fit = function (cv.fit, mod) {
  # plot linear regression result
  glmcoef       = coef(mod, cv.fit$lambda.min)
  coef.increase = dimnames(glmcoef[glmcoef[,1]>0,0])[[1]]
  coef.decrease = dimnames(glmcoef[glmcoef[,1]<0,0])[[1]]
  # get ordered list of variables as they appear at smallest lambda
  allnames = names(coef(mod)[ ,ncol(coef(mod))][order(coef(mod)[ ,ncol(coef(mod))], decreasing=TRUE)])
  # remove intercept
  allnames = setdiff(allnames, allnames[grep("Intercept",allnames)])
  # assign colors
  cols = rep("gray", length(allnames))
  cols[allnames %in% coef.increase] = "red"      # higher mpg is good
  cols[allnames %in% coef.decrease] = "blue"     # lower mpg is not
  plot_glmnet(cv.fit$glmnet.fit, label=TRUE, s=cv.fit$lambda.min, col=cols)
}

