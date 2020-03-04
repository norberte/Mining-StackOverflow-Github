
setwd("C:/Users/Norbert/Desktop/thesis work/RQ2-4/RQ4")

library(readr)
library(dplyr)
library(inspectdf)
library(skimr)
library(ggplot2)
library(grDevices)

GH_past_GH_recent <- read_csv("C:/Users/Norbert/Desktop/thesis work/RQ2-4/RQ4/RQ4_GH_past_to_GH_recent.csv")
SO_past_SO_recent <- read_csv("C:/Users/Norbert/Desktop/thesis work/RQ2-4/RQ4/RQ4_SO_past_to_SO_recent.csv")


dataset_name = "SO past-recent"




par(mfrow=c(1,1))
d <- ggplot(SO_past_SO_recent, aes(as.numeric(na.omit(SO_past_SO_recent$`Jaccard Distance`)))) + geom_density(fill = "grey") + 
  labs(title=paste0("Density Plot for ", dataset_name)) +
  labs(x="Jaccard Distances (0-1)", y="Density Estimate") + theme_bw()


d
h <- hist(SO_past_SO_recent$`Jaccard Distance`,plot=FALSE)
h$density = h$counts/sum(h$counts)
his <- data.frame(breaks = seq(0.05, 1, 0.05), percentage = h$density * 100) 


g <- ggplot(his, aes(x = breaks, y = percentage)) + geom_bar(color = "black", fill="grey", stat = "identity") + 
  labs(title=paste0("Histogram of ", dataset_name)) +
  labs(x="Jaccard Distances (0-1)", y="Relative Percentage") + theme_bw()

ggarrange(d,g, labels = c("A", "B"), ncol = 2, nrow = 1)



groups<-c(0, 0.2, 0.4, 0.6, 0.8, 1)
tmp <- cut(as.numeric(na.omit(SO_past_SO_recent$`Jaccard Distance`)), breaks=groups, include.lowest=TRUE)

#the actual code
x <- barplot(prop.table(table(tmp)), names.arg = c("No change", "Slight", "Moderate", "Large", "Very Large"), 
             main = paste0("Change Levels in ", dataset_name), legend.text = TRUE,
             args.legend=list(x = "topright", inset=c(0.02, 0)), col = gray.colors(5), 
             xlab = "Change Levels based on Jaccard Distance scores (0-1)", ylab = "Percent rate")
y <-as.matrix(prop.table(table(tmp)))
text(x,y - 0.01,labels=as.character(round(y, digits=2)))



















d <- ggplot(GH_past_GH_recent, aes(as.numeric(na.omit(GH_past_GH_recent$`Jaccard Distance`)))) + geom_density()
ggsave(filename = paste0("DensityPlot_JaccardDistance_", dataset_name, ".pdf"), plot = d, device = "pdf")


#ggsave(filename = paste0(out_path, "BarPlot_JaccardDistance_", dataset_name, ".pdf"), plot = x, device = "pdf", width = 20, height = 20, units = "cm")

# Histograms ------------------------
p <- ggplot(data=GH_past_GH_recent, aes(as.numeric(na.omit(`Jaccard Distance`)))) + 
  geom_histogram(binwidth = 0.05, col="red", fill="green", alpha = .2) + 
  labs(title=paste0("Histogram of Jaccard Distance for ", dataset_name)) +
  labs(x="Jaccard Distance (0-1)", y="Count")

ggsave(filename = paste0("Histogram_JaccardDistance_", dataset_name, ".pdf"), plot = p, device = "pdf")


h <- hist(as.numeric(na.omit(GH_past_GH_recent$`Jaccard Distance`)),plot=FALSE)
h$density = h$counts/sum(h$counts)
p <- plot(h, freq=FALSE, ylab='Percent rate', xlab = "Jaccard Distance (0-1)", 
          main = paste0("Histogram Jaccard Distance for ", dataset_name), col="green")

ggsave(filename = paste0("PercentRate_Histogram_JaccardDistance_", dataset_name, ".pdf"), plot = p, device = "pdf")


