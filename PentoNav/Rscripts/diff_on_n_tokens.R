library(lme4)
library(emmeans)

filename = commandArgs(trailingOnly=TRUE)
dataset = read.csv(filename) #r_pento.csv, r_features_played.csv, r_features3.csv


# file id,design,level,batch position,accuracy,target,lag to typing,lag to description,n tokens,n adjectives,n adverbs,n nouns


# Fixed & Random factors
# Fixed: 'design', 'accuracy'
# Random: 'file_id' (participant id), 'target', batch_position, level
variable = 'n_tokens'

# Null model
print("NULL MODEL ####################")
null_model <- lmer(
    get(variable) ~ (1|target)
                  + (1|file_id) 
                  + (1|batch_position) 
                  + (1|design),
    data=dataset,
    REML=FALSE
)
summary(null_model)


# Design/Installment/Sec model
print("DESIGN MODEL ###################")
design_model <- lmer(
    get(variable) ~ level
                  + (1|target)
                  + (1|file_id) 
                  + (1|batch_position)
                  + (1|design),
    data=dataset,
    REML=FALSE
)
summary(design_model)


# Compare model1 to null
print("ANOVA TEST ####################")
anova(design_model, null_model)


# Pairwise comparisons
print("EMMEANS ######################")
emmeans(design_model, pairwise ~ design, adjust="tukey")
