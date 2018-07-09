# Basic configurations
BeatWorkloadPath <- "/Users/woodie/Desktop/Atlanta-Zoning/data/workload_by_beat.csv"
BeatCensusPath   <- "/Users/woodie/Desktop/Atlanta-Zoning/temp/census_by_beat.csv"

# Read workload by beat into a matrix
BeatWorkloadRawdata <- read.csv(file=BeatWorkloadPath, sep=",")
WorkloadMat         <- as.matrix(BeatWorkloadRawdata)

# Read census data by beat into a matrix
BeatCensusRawdata <- read.csv(file=BeatCensusPath, sep=",")
CensusMat         <- as.matrix(BeatCensusRawdata)

years <- c(2014, 2015, 2016)

# Preparation of training Xs
Xs <- subset(CensusMat, 
             (CensusMat[,"beat"] %in% WorkloadMat[,"beat"]) & 
             (CensusMat[,"year"] %in% years))
Xs <- Xs[order(Xs[,1], Xs[,2]),] # Reorder Xs by their beats and years

row_inds <- 1:dim(WorkloadMat)[1]
col_inds <- 3:(length(years)+2)

# Preparation of training Ys
ys    <- matrix(nrow=dim(Xs)[1], ncol=3) # Init ys
y_ind <- 1
for (row_ind in row_inds) {
  for (col_ind in col_inds) {
    ys[y_ind, 1] <- WorkloadMat[row_ind, 1]
    ys[y_ind, 2] <- years[col_ind-2]
    ys[y_ind, 3] <- WorkloadMat[row_ind, col_ind]
    y_ind <- y_ind + 1
  }
}

# Preparation of training Xs of the workload in last year
XsLastWorkload <- matrix(nrow=dim(Xs)[1], ncol=3)
x_ind          <- 1
for (row_ind in row_inds) {
  for (col_ind in col_inds) {
    XsLastWorkload[x_ind, 1] <- WorkloadMat[row_ind, 1]
    XsLastWorkload[x_ind, 2] <- years[col_ind-2] - 1
    XsLastWorkload[x_ind, 3] <- WorkloadMat[row_ind, col_ind-1]
    x_ind <- x_ind + 1
  }
}

# Take workload in last year into consideration
Xs <- cbind(Xs, XsLastWorkload[,3])
colnames(Xs)[15] <- "workload.last.year"

library(glmnet)
lr    <- lm(ys[,3]~Xs[,2:15])
lasso <- glmnet(Xs[,2:15], ys[,3], alpha = 1)