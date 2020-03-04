
setwd("C:/Users/Norbert/Desktop/thesis work/RQ2-4/RQ2")
library(readr)
library(dplyr)
library(inspectdf)
library(skimr)
library(ggplot2)
library(grDevices)

GH_SO_past <- read_csv("C:/Users/Norbert/Desktop/thesis work/RQ2-4/RQ2/RQ2_3_GH_SO_past_word_regr_data.csv")

GH_SO_recent <- read_csv("C:/Users/Norbert/Desktop/thesis work/RQ2-4/RQ2/RQ2_3_GH_SO_recent_word_regr_data.csv")


dataset_name = "GH_recent - SO_recent"


########################################### jaccard_similarity #######################################################

# ---------- Density plot ------------

par(mfrow=c(1,1))
d <- ggplot(GH_SO_recent, aes(as.numeric(na.omit(jaccard_similarity)))) + geom_density(fill = "grey") + 
  labs(title=paste0("Density Plot for ", dataset_name)) +
  labs(x="Jaccard Similarity (0-1)", y="Density Estimate") + theme_bw()



#ggsave(filename = paste0("BarPlot_jaccard_sim", dataset_name, ".pdf"), plot = x, device = "pdf", width = 20, height = 20, units = "cm")

# Histograms ------------------------
#
#p <- plot(h, freq=FALSE, ylab='Percent rate', xlab = "Jaccard Similarity (0-1)", 
#          main = paste0("Histogram of Word Regr. jaccard_sim for ", dataset_name), col="green")

# ggsave(filename = paste0("PercentRate_Histogram_jaccard_sim_", dataset_name, ".pdf"), plot = p, device = "pdf", width = 20, height = 20, units = "cm")



h <- hist(GH_SO_recent$jaccard_similarity,plot=FALSE)
h$density = h$counts/sum(h$counts)
his <- data.frame(breaks = seq(0.05, 1, 0.05), percentage = h$density * 100) 


g <- ggplot(his, aes(x = breaks, y = percentage)) + geom_bar(color = "black", fill="grey", stat = "identity") + 
  labs(title=paste0("Histogram of ", dataset_name)) +
  labs(x="Jaccard Similarity (0-1)", y="Relative Percentage") + theme_bw()

ggarrange(d,g, labels = c("A", "B"), ncol = 2, nrow = 1)




f <- ggplot(GH_SO_past, aes(as.numeric(na.omit(jaccard_similarity)))) + geom_density(color = "black", fill="grey") + theme_bw()
f

# Bar plot ------------------
groups<-c(0, 0.2, 0.4, 0.6, 0.8, 1)
tmp <- cut(as.numeric(na.omit(GH_SO_recent$jaccard_similarity)), breaks=groups, include.lowest=TRUE)

x <- barplot(prop.table(table(tmp)), names.arg = c("No Overlap", "Slight", "Moderate", "Large", "Very Large"), 
             main = paste0("Overlap Levels in ", dataset_name), legend.text = TRUE,
             col = heat.colors(5), xlab = "Overlap Levels based on Jaccard similarity scores (0-1)", ylab = "Percent rate")
y <-as.matrix(prop.table(table(tmp)))
text(x,y - 0.015,labels=as.character(round(y, digits=2)))
  



  
  


#p <- ggplot(h, aes(as.numeric(na.omit(jaccard_similarity)))) + 
#  geom_histogram(binwidth = 0.05, col="red", fill="green", alpha = .2) + 
#  labs(title=paste0("Histogram of Word Regr. jaccard_sim for ", dataset_name)) +
#  labs(x="Jaccard_sim (0-1)", y="Count")

#ggsave(filename = paste0("Frequency_Histogram_jaccard_sim_", dataset_name, ".pdf"), plot = p, device = "pdf")











dataset_name = "GH_SO_past"


########################################### jaccard_similarity #######################################################

# ---------- Density plot ------------
d <- ggplot(GH_SO_past, aes(as.numeric(na.omit(jaccard_similarity)))) + geom_density() + 
  labs(title=paste0("Density Plot of Jaccards similarities for ", dataset_name)) +
  labs(x="Jaccard_similarity (0-1)", y="Density Estimate")
ggsave(filename = paste0("DensityPlot_jaccard_sim_", dataset_name, ".pdf"), plot = d, device = "pdf")


# Bar plot ------------------
groups<-c(0, 0.2, 0.4, 0.6, 0.8, 1)
tmp <- cut(as.numeric(na.omit(GH_SO_past$jaccard_similarity)), breaks=groups, include.lowest=TRUE)

x <- barplot(prop.table(table(tmp)), names.arg = c("No overlap", "Slight Ov.", "Moderate", "Large Ov.", "Very Large"), 
             main = paste0("TopicWord jaccard_sim in ", dataset_name, " Word Regr."), legend.text = TRUE,
             col = heat.colors(5), xlab = "Jaccards similarity Levels (0-1)", ylab = "Percent rate")
y <-as.matrix(prop.table(table(tmp)))
text(x,y - 0.012,labels=as.character(round(y, digits=2)))
#ggsave(filename = paste0("BarPlot_jaccard_sim", dataset_name, ".pdf"), plot = x, device = "pdf", width = 20, height = 20, units = "cm")

# Histograms ------------------------
h <- hist(GH_SO_past$jaccard_similarity,plot=FALSE)
h$density = h$counts/sum(h$counts)
p <- plot(h, freq=FALSE, ylab='Percent rate', xlab = "Jaccard Similarity (0-1)", 
          main = paste0("Histogram of Word Regr. jaccard_sim for ", dataset_name), col="green", fill="green", alpha = .2)

ggsave(filename = paste0("PercentRate_Histogram_jaccard_sim_", dataset_name, ".pdf"), plot = p, device = "pdf", width = 20, height = 20, units = "cm")


p <- ggplot(data=GH_SO_past, aes(as.numeric(na.omit(jaccard_similarity)))) + 
  geom_histogram(binwidth = 0.05, col="red", fill="green", alpha = .2) + 
  labs(title=paste0("Histogram of Word Regr. jaccard_sim for ", dataset_name)) +
  labs(x="Jaccard_sim (0-1)", y="Count")

ggsave(filename = paste0("Frequency_Histogram_jaccard_sim_", dataset_name, ".pdf"), plot = p, device = "pdf")




