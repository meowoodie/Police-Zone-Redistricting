# R script
# 
# By Shixiang Zhu
# Contact: shixiang.zhu@gatech.edu

root.dir = 'Desktop/workspace/Zoning-Analysis'
raw.911calls.path = paste(root.dir, 'data/APDORR Gwinn-Villaroel ICIS Data Pull.xlsx', sep='/')

source(paste(root.dir, 'heuristic/lib/combopt.R', sep='/'))
source(paste(root.dir, 'heuristic/lib/preproc.R', sep='/'))

top.K = 30
zone  = '7'

# read excel data into dataframe
library('readxl')
raw.911calls.type = c('text', 'text', 'text', 'date', 'date', 'date', 
                      'date', 'text', 'text', 'text', 'text')
raw.911calls.data = read_excel(raw.911calls.path, col_types=raw.911calls.type)

# define theme for bar chart
my_theme <- function(){
  theme_light() +
    theme(text = element_text(),  
          plot.title = element_text(size = 13, color = "gray30"),   # Set up the title style
          plot.subtitle = element_text(size = 11, color = "black"), # Set up the subtitle style
          plot.margin = unit(c(0.5,0,0,2.5), "cm"),                 # Add white space at the top and left
          panel.grid = element_blank(),
          panel.border = element_blank(),
          axis.title = element_blank(),
          axis.ticks = element_blank(),
          axis.text.x = element_blank(),
          axis.text.y = element_text(size = 9, color = "gray10"))
}

# ---------------------------------------------------------------------------------------------------------------------

library('dplyr')
library("ggplot2")
# count of each of categories
categories.count      = raw.911calls.data %>% 
  group_by(Zone, Offense_Descripton) %>% 
  count() %>% 
  as.data.frame
zone.categories.count = categories.count[categories.count$Zone==zone, c('Offense_Descripton', 'n')]
zone.categories.count$percentage = sprintf("%.1f%%", 100*(zone.categories.count$n / sum(zone.categories.count$n)))
zone.categories.count$highlight  = rep(0, nrow(zone.categories.count))     # init highlight field
zone.categories.count[which.max(zone.categories.count$n), 'highlight'] = 1 # set 1 for the entry with maximum count
# sort dataframe and select top K entries
zone.categories.count = zone.categories.count[rev(order(zone.categories.count$n)), ]
zone.categories.count = zone.categories.count[1:top.K, ]
# calculate the total sales and make it nicely formatted. This could be embedded
# in the ggtitle() call, but it gets a little messy
total_count = paste0('Total Incidents: ',
                     format(sum(zone.categories.count$n), big.mark = ","))
# Create the actual plot
ggplot(zone.categories.count, aes(x = reorder(Offense_Descripton, n), y = n)) + 
  ggtitle(sprintf("What Is the Count of Incidents in Zone %s?", zone), # Add the title and subtitle
          subtitle = total_count) +                                    # to the plot
  geom_bar(stat = "identity", 
           fill = "gray90",     
           width = 0.75) +
  geom_text(aes(label = percentage),
            size = 3.5,                 
            hjust = 0) +
  coord_flip() +
  scale_y_continuous(expand = c(0, 0),
                     limits = c(0, max(zone.categories.count$n) * 1.3)) +
  my_theme()

# ---------------------------------------------------------------------------------------------------------------------

# average workload of each of categories
categories.workload = raw.911calls.data %>% 
  mutate(Workload = (Approved_Date - Report_Date) + (Approved_Time - Report_Time)) %>% 
  group_by(Zone, Offense_Descripton) %>%
  summarize(Avg_Workload = sum(Workload, na.rm = TRUE)) %>%
  as.data.frame
zone.categories.workload = categories.workload[categories.workload$Zone==zone, c('Offense_Descripton', 'Avg_Workload')]
zone.categories.workload$Avg_Workload_Hr = sprintf("%.2f hours", zone.categories.workload$Avg_Workload / 3600)
zone.categories.workload$highlight = rep(0, nrow(zone.categories.workload))     # init highlight field
zone.categories.workload[which.max(zone.categories.workload$Avg_Workload), 'highlight'] = 1 # set 1 for the entry with maximum count
# sort dataframe and select top K entries
zone.categories.workload = zone.categories.workload[rev(order(zone.categories.workload$Avg_Workload)), ]
zone.categories.workload = zone.categories.workload[1:top.K, ]

# Create the actual plot
ggplot(zone.categories.workload, aes(x = reorder(Offense_Descripton, Avg_Workload), y = Avg_Workload)) + 
  ggtitle(sprintf("Total Workload of Each Category in Zone %s", zone)) + # Add the title and subtitle to the plot
  geom_bar(stat = "identity", 
           fill = "gray90",     
           width = 0.75) +
  geom_text(aes(label = Avg_Workload_Hr),
            size = 3.5,                 
            hjust = 0) +
  coord_flip() +
  scale_y_continuous(expand = c(0, 0),
                     limits = c(0, max(zone.categories.workload$Avg_Workload) * 1.3)) +
  my_theme()
