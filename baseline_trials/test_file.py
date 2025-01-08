import random

print(random.sample([1, 2, 3], 3)[1])





### Generate trial structure

# ## 1) Baseline trials
# trials_DG = random.sample(['DG give', 'DG give norm'], 2)
# trials_3PP = random.sample(['3PP give', '3PP punish', '3PP punish norm'], 3)
# trials_2PP = random.sample(['2PP give', '2PP punish', '2PP punish norm'], 3)
# trials_3PR = random.sample(['3PR give',  '3PR reward', '3PR reward norm'], 3)
# trials_3PC = random.sample(['3PC give', '3PC comp', '3PC comp norm'], 3)
# order_baseline = random.sample([trials_3PP, trials_2PP, trials_3PR, trials_3PC], 4)
# order_baseline_flat = [item for sublist in order_baseline for item in sublist] # Flatten the nested lists
# trials_baseline = trials_DG + order_baseline_flat
#
# ## 2) Ingroup - outgroup trials
# trials_3PP_INOUT = random.sample(['3PP give IN', '3PP give OUT', '3PP give norm IN', '3PP give norm OUT',
#                     '3PP punish IN IN', '3PP punish IN OUT', '3PP punish OUT IN', '3PP punish OUT OUT',
#                     '3PP punish norm IN IN', '3PP punish norm OUT OUT'], 10)
# trials_3PR_INOUT = random.sample(['3PR give IN', '3PR give OUT', '3PR give norm IN', '3PR give norm OUT',
#                     '3PR punish IN IN', '3PR punish IN OUT', '3PR punish OUT IN', '3PR punish OUT OUT',
#                     '3PR punish norm IN IN', '3PR punish norm OUT OUT'], 10)
# trials_3PC_INOUT = random.sample(['3PC give IN', '3PC give OUT', '3PC give norm IN', '3PC give norm OUT',
#                     '3PC punish IN IN', '3PC punish IN OUT', '3PC punish OUT IN', '3PC punish OUT OUT',
#                     '3PC punish norm IN IN', '3PC punish norm OUT OUT'], 10)
# order_INOUT = random.sample([trials_3PP_INOUT, trials_3PR_INOUT, trials_3PC_INOUT], 3)
# order_INOUT_flat = [item for sublist in order_INOUT for item in sublist] # Flatten the nested lists

## 3) Partner country trials

CURRENT_COUNTRY = 'us'

# # Load country codes
# with open('TPP_game/country_codes.txt', 'r') as file:
#     COUNTRY_LIST = [line.strip() for line in file]

COUNTRY_LIST = ['us', 'ae', 'bl']


print("3PP" in  ('us bl 3PP'))


country_list_no_current = [entry for entry in COUNTRY_LIST if entry != CURRENT_COUNTRY]

print(country_list_no_current)


# Make all possible combinations
combinations = [(x, y) for x in COUNTRY_LIST for y in COUNTRY_LIST]

#print(combinations)

test = [entry for entry in COUNTRY_LIST if entry != CURRENT_COUNTRY]



# Add info on homogenous or heterogeneous outgroups
combinations = [(x, y, x == y) for x, y in combinations]

# Every participant should get specific KINDS of trials





# Add trial types
in_out_trials = [entry for entry in combinations if entry[0] == CURRENT_COUNTRY]
out_in_trials = [entry for entry in combinations if entry[1] == CURRENT_COUNTRY]
out_out_homog_trials = [entry for entry in combinations if (entry[0] != CURRENT_COUNTRY and entry[1] != CURRENT_COUNTRY and entry[2] ) ]
out_out_heterog_trials = [entry for entry in combinations if (entry[0] != CURRENT_COUNTRY and entry[1] != CURRENT_COUNTRY and entry[2] == False ) ]


def sample_trials_partner(pool, num_trials, pool_name):
    # If empty, refill from the original pool
    if len(pool) < num_trials:
        pool = eval(pool_name).copy()
    # Otherwise, keep sampling without replacement
    trials = random.sample(pool, num_trials)
    for trial in trials:
        pool.remove(trial)
    return trials, pool


# a) Dictator role

number_trials_partner_dic_out = 2


# Make country list without current country
country_list_no_current = [entry for entry in COUNTRY_LIST if entry != CURRENT_COUNTRY]
country_list_no_current_editable = country_list_no_current.copy()


trials_partner_dic_out_current, country_list_no_current_editable = sample_trials_partner(country_list_no_current_editable,
                                                       number_trials_partner_dic_out, "country_list_no_current")

#print(trials_partner_dic_out_current)

trials_partner_dic_out_current2, country_list_no_current_editable = sample_trials_partner(country_list_no_current_editable,
                                                       number_trials_partner_dic_out, "country_list_no_current")

#print(trials_partner_dic_out_current2)

trials_partner_dic_out_current3, country_list_no_current_editable = sample_trials_partner(country_list_no_current_editable,
                                                       number_trials_partner_dic_out, "country_list_no_current")

#print(trials_partner_dic_out_current3)

trials_partner_dic_out_current4, country_list_no_current_editable = sample_trials_partner(country_list_no_current_editable,
                                                       number_trials_partner_dic_out, "country_list_no_current")

#print(trials_partner_dic_out_current4)

trials_partner_dic_out_current5, country_list_no_current_editable = sample_trials_partner(country_list_no_current_editable,
                                                       number_trials_partner_dic_out, "country_list_no_current")

#print(trials_partner_dic_out_current5)




# print(in_out_trials)
# print(out_in_trials)
# print(out_out_homog_trials)
# print(out_out_heterog_trials)


# Sample

# Figure out how to distribute across participants the different combos. Perhaps load from csv generated by R.


#  =
# trials_3PP_INOUT = random.sample(['3PP give IN', '3PP give OUT', '3PP give IN norm', '3PP give OUT norm',
#                     '3PP punish IN IN', '3PP punish IN OUT', '3PP punish OUT IN', '3PP punish OUT OUT',
#                     '3PP punish IN IN norm', '3PP punish OUT OUT norm'], 10)
#
# order_INOUT = random.sample([trials_3PP_INOUT, trials_3PR_INOUT, trials_3PC_INOUT], 3)
# order_INOUT_flat = [item for sublist in order_INOUT for item in sublist] # Flatten the nested lists


