library(tidyr)
data$subject_id <- as.factor(data$subject_id)
data$block <- as.factor(data$block)
# 让数据框包含所有可能的 subject_id 和 block 组合
data_complete <- data %>%
  complete(subject_id = as.factor(c(2:15)), block = as.factor(c(0:11)), condition = c("self", "other"), fill = list(rt = NA))

# 查看结果
head(data_complete)

library(bruceR)  
library(afex)
library(tidyverse)

# 进行重复测量方差分析
result <- aov_ez(id = "subject_id",  # 被试 ID
                 dv = "rt",     # 因变量
                 within = c("condition", "block"),# 重复测量自变量
                 data = data_complete)
summary(result)


library(emmeans)

# 计算条件和区块的边际均值
emmeans(result, pairwise ~ condition | block, adjust = "bonferroni")

emmeans(result, pairwise ~ condition, adjust = "bonferroni")

emmeans(result, pairwise ~ block, adjust = "bonferroni")

emmeans(result, pairwise ~ block | condition, adjust = "bonferroni")

# 查看结果
summary(emmeans_results)


ggplot(data_complete, aes(x=block, y=rt, color=condition, group=condition)) + 
  stat_summary(fun=mean, geom="line", size=1) + 
  stat_summary(fun.data=mean_cl_normal, geom="errorbar", width=0.2) + 
  scale_color_brewer(palette="Set1") + 
  labs(x="block", y="reaction time (ms)", color="condition") + 
  theme_minimal() + 
  theme(panel.background = element_blank(),  # 去除绘图区背景
        plot.background = element_blank())   # 去除整体背景



# 提取对比结果并转换为数据框
contrast_data <- as.data.frame(emmeans(result, pairwise ~ condition | block)$contrasts)

# 处理区块名称（去掉"X"前缀）
contrast_data$block <- as.numeric(gsub("X", "", contrast_data$block))

# 创建显著性标记列
contrast_data <- contrast_data %>%
  mutate(signif = case_when(
    p.value < 0.001 ~ "***",
    p.value < 0.01 ~ "**",
    p.value < 0.05 ~ "*",
    TRUE ~ ""
  ))

# 绘制对比结果
ggplot(contrast_data, aes(x = block, y = estimate)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  geom_errorbar(aes(ymin = estimate - SE*1.96,
                    ymax = estimate + SE*1.96),
                width = 0.2, color = "steelblue") +
  geom_point(size = 3, color = "steelblue") +
  geom_text(aes(label = signif, y = estimate + SE*2.5), 
            size = 6, color = "red") +
  scale_x_continuous(breaks = 0:11) +
  labs(x = "block", 
       y = "Difference Estimates (Other - Self)",
       caption = "Error bars represent 95% confidence interval, * indicates p < 0.05") +
  theme_classic() +
  theme(plot.title = element_text(hjust = 0.5))


# ---------------------------------------------------------------------------- #

# 读取正确率数据
accuracy_data <- read.csv("Output/3_Exp_processed_data/accuracy_data.csv")

# 转换因子变量
accuracy_data$subject_id <- as.factor(accuracy_data$subject_id)
accuracy_data$block <- as.factor(accuracy_data$block)

# 让数据框包含所有可能的 subject_id 和 block 组合
accuracy_data_complete <- accuracy_data %>%
  complete(subject_id = as.factor(c(2:15)), 
           block = as.factor(c(0:11)), 
           condition = c("self", "other"), 
           fill = list(accuracy = NA)) 

# 进行重复测量方差分析
result_acc <- aov_ez(id = "subject_id",  
                          dv = "accuracy",     
                          within = c("condition", "block"), 
                          data = accuracy_data_complete)

# 查看方差分析结果
summary(result_acc)


# 事后检验
# 条件主效应
emmeans(result_acc, pairwise ~ condition, adjust = "bonferroni")

# 区块主效应
emmeans(result_acc, pairwise ~ block, adjust = "bonferroni")

# 条件×区块交互作用
interaction_effects <- emmeans(result_acc, pairwise ~ condition | block, adjust = "bonferroni")


contrast_data <- as.data.frame(interaction_effects$contrasts) %>%
  mutate(
    block = as.numeric(gsub("X", "", block)),  # 处理区块名称
    signif = case_when(
      p.value < 0.001 ~ "***",
      p.value < 0.01 ~ "**",
      p.value < 0.05 ~ "*",
      TRUE ~ "")
  )

ggplot(contrast_data, aes(x = block, y = estimate)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  geom_errorbar(aes(ymin = estimate - SE*1.96, ymax = estimate + SE*1.96),
                width = 0.2, color = "steelblue") +
  geom_point(size = 3, color = "steelblue") +
  geom_text(aes(label = signif, y = estimate + SE*2.5), 
            size = 6, color = "red", vjust = 0.5) +
  scale_x_continuous(breaks = 0:11) +
  labs(x = "Block", 
       y = "Accuracy Difference (Other - Self)",
       caption = "Error bars: 95% CI, * p < 0.05") +
  theme_classic(base_size = 12) +
  theme(plot.title = element_text(hjust = 0.5))


# 1. 条件×区块趋势图
ggplot(accuracy_data_complete, aes(x=block, y=accuracy, color=condition, group=condition)) +
  stat_summary(fun=mean, geom="line", size=1) +
  stat_summary(fun.data=mean_cl_normal, geom="errorbar", width=0.2) +
  scale_color_brewer(palette="Set1") +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +  # 转换为百分比格式
  labs(x="Block", y="Accuracy", color="Condition",
       title="Accuracy across Blocks by Condition") +
  theme_classic(base_size = 14) +
  theme(legend.position = "top")