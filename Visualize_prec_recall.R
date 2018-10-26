library(readr)
library(ggplot2)
library(dplyr)

FC1_poly <- read_csv("~/Documents/MIREX/MIREX2018/Evaluation/FC1/poly/FC1_poly.csv")
FC1_poly$F1_pitch <- 2 * FC1_poly$prec_pitch * FC1_poly$rec_pitch / (FC1_poly$prec_pitch + FC1_poly$rec_pitch)
FC1_poly$F1_ioi <- 2 * FC1_poly$prec_ioi * FC1_poly$rec_ioi / (FC1_poly$prec_ioi + FC1_poly$rec_ioi)
FC1_poly$F1_pairs <- 2 * FC1_poly$prec_pairs * FC1_poly$rec_pairs / (FC1_poly$prec_pairs + FC1_poly$rec_pairs)
FC1_poly$alg <- "FC1"

FC1_imp_poly <- read_csv("~/Documents/MIREX/MIREX2018/Results/FC1/output_poly/2/res.csv")
nrow(FC1_imp_poly[FC1_imp_poly$True=="True",])/nrow(FC1_imp_poly)


baseline_poly <- read_csv("~/Documents/MIREX/MIREX2018/Evaluation/Baseline/poly/baseline_poly.csv")
baseline_poly$F1_pitch <- 2 * baseline_poly$prec_pitch * baseline_poly$rec_pitch / (baseline_poly$prec_pitch + baseline_poly$rec_pitch)
baseline_poly$F1_ioi <- 2 * baseline_poly$prec_ioi * baseline_poly$rec_ioi / (baseline_poly$prec_ioi + baseline_poly$rec_ioi)
baseline_poly$F1_pairs <- 2 * baseline_poly$prec_pairs * baseline_poly$rec_pairs / (baseline_poly$prec_pairs + baseline_poly$rec_pairs)
baseline_poly$alg <- "MM1"

all_poly <- rbind(FC1_poly,baseline_poly)

cols <- c("MM1" = "#ffffbf", "FC1" = "#fc8d59", "EN1" = "#91bfdb")

ggplot(all_poly, aes(onset, F1_pitch, colour=alg)) + geom_smooth() + 
  xlab("Onset in quarter notes") + ylab("F1(pitch)") + 
  labs(colour="Algorithm", title="F1 of generated pitches, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_F1_pitch.png", width=6, height=4, units="in")
ggplot(all_poly, aes(onset, F1_ioi, colour=alg)) + geom_smooth() + 	
  xlab("Onset in quarter notes") + ylab("F1(ioi)") + 
  labs(colour="Algorithm", title="F1 of generated inter-onset intervals, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_F1_ioi.png", width=6, height=4, units="in")
ggplot(all_poly, aes(onset, F1_pairs, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("F1(pitch-ioi pairs)") + 
  labs(colour="Algorithm", title="F1 of generated pitch-ioi pairs, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_F1_pairs.png", width=6, height=4, units="in")
ggplot(all_poly, aes(onset, prec_pitch, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Precision(pitch)") + 
  labs(colour="Algorithm", title="Precision of generated pitches, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_P_pitch.png", width=6, height=4, units="in")
ggplot(all_poly, aes(onset, prec_ioi, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Precision(ioi)") + 
  labs(colour="Algorithm", title="Precision of generated inter-onset intervals, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_P_ioi.png", width=6, height=4, units="in")
ggplot(all_poly, aes(onset, prec_pairs, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Precision(pitch-ioi pairs)") + 
  labs(colour="Algorithm", title="Precision of generated pitch-ioi pairs, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_P_pairs.png", width=6, height=4, units="in")
ggplot(all_poly, aes(onset, rec_pitch, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Recall(pitch)") + 
  labs(colour="Algorithm", title="Recall of generated pitches, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_R_pitch.png", width=6, height=4, units="in")
ggplot(all_poly, aes(onset, rec_ioi, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Recall(ioi)") + 
  labs(colour="Algorithm", title="Recall of generated inter-onset intervals, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_R_ioi.png", width=6, height=4, units="in")
ggplot(all_poly, aes(onset, rec_pairs, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Recall(pitch-ioi pairs)") + 
  labs(colour="Algorithm", title="Recall of generated pitch-ioi pairs, polyphonic") +
  scale_colour_manual(values = cols)
ggsave("2018_poly_R_pairs.png", width=6, height=4, units="in")

baseline_mono <- read_csv("~/Documents/MIREX/MIREX2018/Evaluation/Baseline/mono/baseline_mono.csv")
baseline_mono$F1_pitch <- 2 * baseline_mono$prec_pitch * baseline_mono$rec_pitch / (baseline_mono$prec_pitch + baseline_mono$rec_pitch)
baseline_mono$F1_ioi <- 2 * baseline_mono$prec_ioi * baseline_mono$rec_ioi / (baseline_mono$prec_ioi + baseline_mono$rec_ioi)
baseline_mono$F1_pairs <- 2 * baseline_mono$prec_pairs * baseline_mono$rec_pairs / (baseline_mono$prec_pairs + baseline_mono$rec_pairs)
baseline_mono$alg <- "MM1"

baseline_mono %>% group_by(onset) %>%  summarise(n = n(), rec_ioi = mean(rec_ioi, na.rm = TRUE))
baseline_mono %>% group_by(onset) %>%  summarise(n = n(), F1_ioi = mean(F1_ioi, na.rm = TRUE))
baseline_mono %>% group_by(onset) %>%  summarise(n = n(), F1_pitch = mean(F1_pitch, na.rm = TRUE))
baseline_mono %>% group_by(onset) %>%  summarise(n = n(), F1_pairs = mean(F1_pairs, na.rm = TRUE))

FC1_mono <- read_csv("~/Documents/MIREX/MIREX2018/Evaluation/FC1/mono/FC1_mono.csv")
FC1_mono$F1_pitch <- 2 * FC1_mono$prec_pitch * FC1_mono$rec_pitch / (FC1_mono$prec_pitch + FC1_mono$rec_pitch)
FC1_mono$F1_ioi <- 2 * FC1_mono$prec_ioi * FC1_mono$rec_ioi / (FC1_mono$prec_ioi + FC1_mono$rec_ioi)
FC1_mono$F1_pairs <- 2 * FC1_mono$prec_pairs * FC1_mono$rec_pairs / (FC1_mono$prec_pairs + FC1_mono$rec_pairs)

FC1_mono %>% group_by(onset) %>%  summarise(n = n(), rec_ioi = mean(rec_ioi, na.rm = TRUE))
FC1_mono %>% group_by(onset) %>%  summarise(n = n(), F1_ioi = mean(F1_ioi, na.rm = TRUE))
FC1_mono %>% group_by(onset) %>%  summarise(n = n(), F1_pitch = mean(F1_pitch, na.rm = TRUE))
FC1_mono %>% group_by(onset) %>%  summarise(n = n(), F1_pairs = mean(F1_pairs, na.rm = TRUE))
FC1_mono$alg <- "FC1"

FC1_imp_mono <- read_csv("~/Documents/MIREX/MIREX2018/Results/FC1/output_mono/2/res.csv")
nrow(FC1_imp_mono[FC1_imp_mono$True=="True",])/nrow(FC1_imp_mono)

EN1_mono <- read_csv("~/Documents/MIREX/MIREX2018/Evaluation/EN1/mono/EN1_mono.csv")
EN1_mono$F1_pitch <- 2 * EN1_mono$prec_pitch * EN1_mono$rec_pitch / (EN1_mono$prec_pitch + EN1_mono$rec_pitch)
EN1_mono$F1_ioi <- 2 * EN1_mono$prec_ioi * EN1_mono$rec_ioi / (EN1_mono$prec_ioi + EN1_mono$rec_ioi)
EN1_mono$F1_pairs <- 2 * EN1_mono$prec_pairs * EN1_mono$rec_pairs / (EN1_mono$prec_pairs + EN1_mono$rec_pairs)
EN1_mono$alg <- "EN1"

EN1_mono %>% group_by(onset) %>%  summarise(n = n(), rec_ioi = mean(rec_ioi, na.rm = TRUE))
EN1_mono %>% group_by(onset) %>%  summarise(n = n(), F1_ioi = mean(F1_ioi, na.rm = TRUE))
EN1_mono %>% group_by(onset) %>%  summarise(n = n(), F1_pitch = mean(F1_pitch, na.rm = TRUE))
EN1_mono %>% group_by(onset) %>%  summarise(n = n(), F1_pairs = mean(F1_pairs, na.rm = TRUE))

all_mono <- rbind(baseline_mono, FC1_mono, EN1_mono)
nrow(all_mono)

ggplot(all_mono, aes(onset, F1_pitch, colour=alg)) + geom_smooth() + 
  xlab("Onset in quarter notes") + ylab("F1(pitch)") + 
  labs(colour="Algorithm", title="F1 of generated pitches, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_F1_pitch.png", width=6, height=4, units="in")
ggplot(all_mono, aes(onset, F1_ioi, colour=alg)) + geom_smooth() + 	
  xlab("Onset in quarter notes") + ylab("F1(ioi)") + 
  labs(colour="Algorithm", title="F1 of generated inter-onset intervals, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_F1_ioi.png", width=6, height=4, units="in")
ggplot(all_mono, aes(onset, F1_pairs, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("F1(pitch-ioi pairs)") + 
  labs(colour="Algorithm", title="F1 of generated pitch-ioi pairs, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_F1_pairs.png", width=6, height=4, units="in")
ggplot(all_mono, aes(onset, prec_pitch, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Precision(pitch)") + 
  labs(colour="Algorithm", title="Precision of generated pitches, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_P_pitch.png", width=6, height=4, units="in")
ggplot(all_mono, aes(onset, prec_ioi, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Precision(ioi)") + 
  labs(colour="Algorithm", title="Precision of generated inter-onset intervals, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_P_ioi.png", width=6, height=4, units="in")
ggplot(all_mono, aes(onset, prec_pairs, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Precision(pitch-ioi pairs)") + 
  labs(colour="Algorithm", title="Precision of generated pitch-ioi pairs, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_P_pairs.png", width=6, height=4, units="in")
ggplot(all_mono, aes(onset, rec_pitch, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Recall(pitch)") + 
  labs(colour="Algorithm", title="Recall of generated pitches, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_R_pitch.png", width=6, height=4, units="in")
ggplot(all_mono, aes(onset, rec_ioi, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Recall(ioi)") + 
  labs(colour="Algorithm", title="Recall of generated inter-onset intervals, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_R_ioi.png", width=6, height=4, units="in")
ggplot(all_mono, aes(onset, rec_pairs, colour=alg)) + geom_smooth() +
  xlab("Onset in quarter notes") + ylab("Recall(pitch-ioi pairs)") + 
  labs(colour="Algorithm", title="Recall of generated pitch-ioi pairs, monophonic") +
  scale_colour_manual(values = cols)
ggsave("2018_mono_R_pairs.png", width=6, height=4, units="in")