library("gamm4")
library("lmerTest")
setwd("~/Documents/UPenn/UPennSenior/WorkStudy/GenderDifference/RModel")

mydata = read.csv("table.csv")
mydata = transform(mydata, FREQUENCY = scale(log10(FREQUENCY)))
mydata = transform(mydata, AGE = scale(AGE))

mod <- gamm4(TENSE ~ GENDER + FREQUENCY + s(AGE, k=4), data=mydata, random = ~ (1|ROOT) + (1|NAME_AND_AUTHOR), family = binomial)

print(summary(mod$gam))

m3 <- gamm4(TENSE ~ s(AGE, k=4) + GENDER,
            random=~(1 | NAME_AND_AUTHOR) + (1 | ROOT), data=mydata, family=binomial)
m4 <- gamm4(TENSE ~ s(AGE, k=4) + FREQUENCY,
            random=~(1 | NAME_AND_AUTHOR) + (1 | ROOT), data=mydata, family=binomial)
m5 <- gamm4(TENSE ~ s(AGE, k=4) + FREQUENCY + GENDER,
            random=~(1 | NAME_AND_AUTHOR) + (1 | ROOT), data=mydata, family=binomial)

# Likelihood ratio test on Target.Freq; manual version of what drop1 does for a variable.
aov <- anova(m3$mer, m5$mer, test="Chisq")
print(aov)

# Likelihood ratio test on GENDER; manual version of what drop1 does for a variable.
aov <- anova(m4$mer, m5$mer, test="Chisq")
print(aov)

save.image("spacy.RData")
