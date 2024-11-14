import numpy as np
import pandas as pd

# Parameters
# The total number of users participating in the simulation. (Platform Users)
num_users = 2500 
# The minimum amount of money a user can have.
min_money = 20 
# The maximum amount of money a user can have.
max_money = 100 
# The increment step for generating random amounts of money for users (e.g., users can have $20, $40, $60, etc.).
increment = 20 
# The proportion of users who will pledge for the campaign, expressed as a percentage
pledge_rate = 1  
# The predefined packages of amounts users can pledge.
pledge_packages = [20, 40, 100] 
# The target amount that the campaign aims to raise.
campaign_goal = 1200
#which the auction bid increases with each bid
bid_increment = 0.01  
# The total duration of the auction phase in days
auction_duration_days = 30

# Bidder Definitions 
# Sniper Bidder: A sniper bidder waits until the last possible moment to place their bid. 
# They bid rarely and strategically, aiming to win the auction by placing a bid just before it ends. 
# This behavior reduces the chances of being outbid by others. 

# Impulse Bidder: An impulse bidder bids frequently and without much consideration. 
# They tend to place bids on a whim, often driven by the excitement of the auction rather than a calculated strategy. 
# Impulse bidders may continue to bid even if the price exceeds their initial expectations. 

# Conservative Bidder: A conservative bidder bids cautiously and stops bidding when the price reaches a certain threshold. 
# They are mindful of the auction price and their budget, preferring not to overextend themselves.

# The probability of a user being a conservative bidder
conservative_probability = 0.50 
# The probability of a user being a sniper bidder
sniper_probability = 0.10 
# The probability of a user being an impulse bidder
impulse_probability = 0.40 
# Conservative bidders stop if the price exceeds this amount
conservative_threshold = 50  
# 25% chance for snipers to place a bid
sniper_chance = 0.25  
# 20% chance for impulse bidders to place a bid
impulse_chance = 0.20  

#Campaign Rate Parameters
campaign_rb_ps_rate = .10
campaign_discout_promo_rate = .80
campaign_operating_costs_rate = .10
campaign_liquidity_pool_rate = .30
overage_referral_bonus_rate = .20
charity_amount_rate = .10
overage_profit_rate = .30
overage_operating_costs_rate = .10


#####################################DO NOT TOUCH BELOW THIS LINE########################################################

# Generate users with random money in increments of 20
user_money = np.random.choice(range(min_money, max_money + increment, increment), num_users)
user_data = pd.DataFrame({
    'User_ID': range(num_users),
    'Money': user_money,
    'Total_Pledges': 0,
    'Points': 0,
    'Bids': 0
})

# Determine users who will pledge (using pledge_rate)
num_pledging_users = int(num_users * pledge_rate)
pledging_users = np.random.choice(user_data.index, num_pledging_users, replace=False)

# Initialize total pledged amount
total_pledged = 0

# Pledging phase - Allow pledges to continue after the campaign goal is met
for user_index in pledging_users:
    user_pledge_total = 0
    user_money = user_data.at[user_index, 'Money']
    # Randomized pledge package selection
    while user_pledge_total + min(pledge_packages) <= user_money:
        pledge = np.random.choice([p for p in pledge_packages if p + user_pledge_total <= user_money])
        user_pledge_total += pledge
        user_data.at[user_index, 'Points'] += pledge
        user_data.at[user_index, 'Total_Pledges'] += pledge
        total_pledged += pledge

# Total money from pledging
total_pledged_amount = user_data['Total_Pledges'].sum()
pledge_overage = max(0, total_pledged_amount - campaign_goal)  # Calculate overage if above the goal

# Conversion of pledges to points and bids
user_data['Bids'] = user_data['Total_Pledges']

# Define user bidding behaviors
# Ensure probabilities add up to 1
probabilities = np.array([conservative_probability, sniper_probability, impulse_probability])
probabilities /= probabilities.sum()

# Track auction information
auction_data = []
current_bid_price = 0.0
user_points = user_data['Bids'].copy()
leading_bidder = None
daily_leader_changes = [0] * auction_duration_days

# User category counters
one_category_users = 0
two_category_users = 0
three_category_users = 0

# Detailed category counters
conservative_only = 0
sniper_only = 0
impulse_only = 0
conservative_sniper = 0
conservative_impulse = 0
sniper_impulse = 0
all_three = 0


# Simulate auction phase over X days
for day in range(auction_duration_days):
    bids_for_day = np.random.randint(100, 10000)
    daily_bidders = np.random.choice(user_data.index, bids_for_day, replace=True)
    
    for bidder in daily_bidders:
        bidder_conservative = np.random.random() < conservative_probability
        bidder_sniper = np.random.random() < sniper_probability
        bidder_impulse = np.random.random() < impulse_probability

        categories_count = int(bidder_conservative) + int(bidder_sniper) + int(bidder_impulse)
        if categories_count == 1:
            one_category_users += 1
            if bidder_conservative:
                conservative_only += 1
            elif bidder_sniper:
                sniper_only += 1
            elif bidder_impulse:
                impulse_only += 1
        elif categories_count == 2:
            two_category_users += 1
            if bidder_conservative and bidder_sniper:
                conservative_sniper += 1
            elif bidder_conservative and bidder_impulse:
                conservative_impulse += 1
            elif bidder_sniper and bidder_impulse:
                sniper_impulse += 1
        elif categories_count == 3:
            three_category_users += 1
            all_three += 1
        
        if bidder_conservative and current_bid_price >= conservative_threshold:
            continue  # Conservative bidder stops if the price is too high
        
        if bidder_sniper and np.random.random() > sniper_chance:
            continue  # Sniper bids occasionally
        
        if bidder_impulse and np.random.random() > impulse_chance:
            continue  # Impulse bidder bids frequently

        if user_points[bidder] > 0:
            current_bid_price += bid_increment
            user_points[bidder] -= 1
            auction_data.append((day, bidder, current_bid_price))
            if leading_bidder != bidder:
                leading_bidder = bidder
                daily_leader_changes[day] += 1

auction_df = pd.DataFrame(auction_data, columns=['Day', 'User_ID', 'Bid_Price'])


# Calculate and print required outputs
total_bidders = auction_df['User_ID'].nunique()
total_pledgers = len(pledging_users)
total_bids = len(auction_df)
unique_bidders = auction_df['User_ID'].nunique()
auction_amount = auction_df['Bid_Price'].max()
average_pledge_per_user = total_pledged_amount / total_pledgers
average_bids_per_bidder = total_bids / unique_bidders
pledging_goal_achievement = (total_pledged_amount / campaign_goal) * 100
most_bids_day = auction_df['Day'].value_counts().idxmax()
most_bids_count = auction_df['Day'].value_counts().max()
referral_bonus_and_profit_sharing = campaign_goal * campaign_rb_ps_rate
discount_promo_marketing = campaign_goal * campaign_discout_promo_rate
campaign_operating_costs = campaign_goal * campaign_operating_costs_rate
liquidity_points = pledge_overage * campaign_liquidity_pool_rate
overage_referral_bonus = pledge_overage * overage_referral_bonus_rate
charity_amount = pledge_overage * charity_amount_rate
overage_profit = pledge_overage * overage_profit_rate
overage_operating_costs = pledge_overage * overage_operating_costs_rate
total_users = one_category_users + two_category_users + three_category_users
percentage_one_category = (one_category_users / total_users) * 100
percentage_two_categories = (two_category_users / total_users) * 100
percentage_three_categories = (three_category_users / total_users) * 100
perc_conservative_only = (conservative_only / one_category_users) * 100 if one_category_users else 0
perc_sniper_only = (sniper_only / one_category_users) * 100 if one_category_users else 0
perc_impulse_only = (impulse_only / one_category_users) * 100 if one_category_users else 0
perc_conservative_sniper = (conservative_sniper / two_category_users) * 100 if two_category_users else 0
perc_conservative_impulse = (conservative_impulse / two_category_users) * 100 if two_category_users else 0
perc_sniper_impulse = (sniper_impulse / two_category_users) * 100 if two_category_users else 0
perc_all_three = (all_three / three_category_users) * 100 if three_category_users else 0


# Campaign Output
print("\n**Campaign and Pledging Statistics**")
print("Total Platform Users: ", num_users)
print("Campaign Goal: $", f"{campaign_goal:,}")
print("Auction Duration:", auction_duration_days, "days")
print("Total Participants: ", int(num_users * pledge_rate))
print("Average Pledge per User: $", f"{average_pledge_per_user:.2f}")

#Auction Statistics
print("\n**Auction Statistics**")
print("Total Bidders:", total_bidders)
print("Total Bids:", total_bids)
print("Average Bids per Bidder: ", f"{average_bids_per_bidder:.2f}")
print("Auction Amount: $", f"{auction_amount:,.2f}")

# Output Auction Volatility and Leader Changes
print("\n**Auction Volatility and Leader Changes**")
print("Daily Leader Changes: ", daily_leader_changes)
print(f"Day with Most Bidding Activity: Day {most_bids_day + 1} with {most_bids_count} bids")
print("Total Leader Changes Throughout Auction: ", sum(daily_leader_changes))

# Output detailed breakdowns
print("\n**User Categories**")
print(f"Percentage of users in 1 category: {percentage_one_category:.2f}%")
print(f"  - Conservative only: {perc_conservative_only:.2f}%")
print(f"  - Sniper only: {perc_sniper_only:.2f}%")
print(f"  - Impulse only: {perc_impulse_only:.2f}%")
print(f"Percentage of users in 2 categories: {percentage_two_categories:.2f}%")
print(f"  - Conservative and Sniper: {perc_conservative_sniper:.2f}%")
print(f"  - Conservative and Impulse: {perc_conservative_impulse:.2f}%")
print(f"  - Sniper and Impulse: {perc_sniper_impulse:.2f}%")
print(f"Percentage of users in all 3 categories: {percentage_three_categories:.2f}%")
print(f"  - All three: {perc_all_three:.2f}%")

# Pledging Output
print("\n**Money in and Stats**")
print("Total Pledgers:", total_pledgers)
print("Total Money from Pledging: $", f"{total_pledged_amount:,.2f}")
print("Pledge Overage: $", f"{pledge_overage:,.2f}")
print("Pledge Goal Achievement: ", f"{pledging_goal_achievement:.2f}%", "(Overage: $", f"{pledge_overage:,.2f})")

## Distributions and Profit
print("\n**Campaign Distributions and Profit**")
print("Campaign Goal: $", f"{campaign_goal:,}")
print("Referral Bonus and Profit Sharing: ",f"${referral_bonus_and_profit_sharing:,.2f}")
print("Discounted Sale and Promo Marketing: ",f"${discount_promo_marketing:,.2f}")
print("Operating Costs and Card Fees: ",f"${campaign_operating_costs:,.2f}")

print("\n**Overage Distributions and Profit**")
print("Overage: $", f"{pledge_overage:,.2f}")
print("Stretch Goals and Liquidity Points: ",f"${liquidity_points:,.2f}")
print("Referral Bonus: ",f"${overage_referral_bonus:,.2f}")
print("Charity: ",f"${charity_amount:,.2f}")
print("Operating Costs and Card Fees: ",f"${overage_operating_costs:,.2f}")
print("Profit: ",f"${overage_profit:,.2f}")
