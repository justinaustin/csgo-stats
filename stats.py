import csv
import pprint

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ECO_VAL = 8500
ANTIECO_VAL = 16250
PISTOLS = ['Deagle', 'Tec9', 'USP', 'CZ', 'DualBarettas', 'P250', 'Glock',
           'P2000', 'FiveSeven']
GERNADES = ['Smoke', 'HE', 'Decoy', 'Flash', 'Molotov', 'Incendiary']
PRIMARY_GUNS = ['Bizon', 'Scar20', 'Gallil', 'SG556', 'M4A4', 'AK47', 'Nova',
                'Swag7', 'G3SG1', 'Negev', 'P90', 'MP7', 'SawedOff', 'Mac10',
                'AUG', 'Famas', 'AWP', 'XM1014', 'M4A1', 'M249', 'Scout',
                'UMP', 'MP9']


def load_data(filename):
    with open(filename) as f:
        rows = [
            {k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)
        ]
    return rows


def generate_headshot_graph(rows, filename="headshot_vs_rank.png"):
    hitboxes = set([i["hitbox"] for i in rows])
    ranks = {}
    for i in rows:
        i["att_rank"] = int(i["att_rank"])
        if i["att_rank"] not in ranks:
            ranks[i["att_rank"]] = {"total": 0}
            for hb in hitboxes:
                ranks[i["att_rank"]][hb] = 0
        ranks[i["att_rank"]][i["hitbox"]] += 1
        ranks[i["att_rank"]]["total"] += 1

    xs = sorted([r for r in ranks])
    ys = [ranks[r]["Head"] / ranks[r]["total"] for r in xs]
    fig = plt.figure()
    plt.plot(xs, ys)
    plt.xticks(xs, xs)
    plt.xlabel("Rank")
    plt.ylabel("Headshot Damage Percentage")
    plt.title("Rank vs Headshot Damage Percentage")
    fig.savefig("headshot_vs_rank.png")


def get_rounds(rows):
    rounds = []
    last_round_seen = -1
    new_round = None
    for i in rows:
        if i['round'] != last_round_seen:
            if new_round:
                rounds.append(new_round)
            last_round_seen = i['round']
            new_round = {
                'file': i['file'],
                'map': i['map'],
                'date': i['date'],
                'round': i['round'],
                'winner_team': i['winner_team'],
                'winner_side': i['winner_side'],
                'bomb_site': i['bomb_site'],
                'is_bomb_planted': i['is_bomb_planted'],
                'ct_eq_val': int(i['ct_eq_val']),
                't_eq_val': int(i['t_eq_val']),
                'avg_match_rank': i['avg_match_rank'],
                'weapons_t': [],
                'weapons_ct': [],
            }
            if i['att_side'] == 'Terrorist':
                new_round['weapons_t'] = [(i['wp'], i['att_id'])]
                new_round['hp_dmg_t'] = int(i['hp_dmg'])
            else:
                new_round['weapons_ct'] = [(i['wp'], i['att_id'])]
                new_round['hp_dmg_ct'] = int(i['hp_dmg'])
        else:
            if i['is_bomb_planted'] == 'True':
                new_round['is_bomb_planted'] = True
                new_round['bomb_site'] = i['bomb_site']
            if i['att_side'] == 'Terrorist':
                if (i['wp'], i['att_id']) not in new_round['weapons_t']:
                    new_round['weapons_t'].append((i['wp'], i['att_id']))
            else:
                if (i['wp'], i['att_id']) not in new_round['weapons_ct']:
                    new_round['weapons_ct'].append((i['wp'], i['att_id']))
    rounds.append(new_round)
    return rounds


def eco_win_percentage(rounds):
    ranks = {}
    for i in rounds:
        if i['avg_match_rank'] not in ranks:
            ranks[i['avg_match_rank']] = {
                't_wins': 0,
                't_losses': 0,
                'ct_wins': 0,
                'ct_losses': 0,
            }
        # check if t eco
        if i['t_eq_val'] <= ECO_VAL and i['ct_eq_val'] >= ANTIECO_VAL:
            if i['winner_side'] == 'Terrorist':
                ranks[i['avg_match_rank']]['t_wins'] += 1
            else:
                ranks[i['avg_match_rank']]['t_losses'] += 1
        elif i['ct_eq_val'] <= ECO_VAL and i['t_eq_val'] >= ANTIECO_VAL:
            if i['winner_side'] == 'Terrorist':
                ranks[i['avg_match_rank']]['ct_losses'] += 1
            else:
                ranks[i['avg_match_rank']]['ct_wins'] += 1

    xs = sorted([r for r in ranks], key=lambda x: int(float(x)))
    ys_t = [ranks[r]['t_wins'] / (ranks[r]['t_wins'] + ranks[r]['t_losses'])
            for r in xs]
    ys_ct = [ranks[r]['ct_wins'] / (ranks[r]['ct_wins'] +
                                    ranks[r]['ct_losses']) for r in xs]
    fig = plt.figure()
    plt.plot(xs, ys_t, label="Terrorist")
    plt.plot(xs, ys_ct, label="Counter-Terrorist")
    plt.xticks(xs, xs)
    plt.xlabel("Rank")
    plt.ylabel("Eco Win Percentage")
    plt.title("Rank vs Eco Win Percentage")
    plt.legend(loc="best")
    fig.savefig("eco_win_vs_rank.png")



def eco_bomb_plant_percentage(rounds):
    ranks = {}
    for i in rounds:
        if i['avg_match_rank'] not in ranks:
            ranks[i['avg_match_rank']] = {
                'bomb_plants': 0,
                'ecos': 0,
            }
        if i['t_eq_val'] <= ECO_VAL and i['ct_eq_val'] >= ANTIECO_VAL:
            ranks[i['avg_match_rank']]['ecos'] += 1
            # if i['is_bomb_planted']: evaluates to True if it is 'False'
            if i['is_bomb_planted'] == True:
                ranks[i['avg_match_rank']]['bomb_plants'] += 1

    xs = sorted([r for r in ranks], key=lambda x: int(float(x)))
    ys = [ranks[r]['bomb_plants'] / ranks[r]['ecos'] for r in xs]
    fig = plt.figure()
    plt.plot(xs, ys)
    plt.xticks(xs, xs)
    plt.xlabel("Rank")
    plt.ylabel("Eco Bomb Plant Percentage")
    plt.title("Rank vs Eco Bomb Plant Percentage")
    fig.savefig("eco_bomb_plant_vs_rank.png")


def pistol_hits_while_having_gun_by_rank(rounds):
    ranks = {}
    for i in rounds:
        if i['avg_match_rank'] not in ranks:
            ranks[i['avg_match_rank']] = {
                'dmg': 0,
                'total': 0,
            }
        weapons = i['weapons_ct'] + i['weapons_t']
        for wp, player in weapons:
            if wp in PISTOLS and any([(w, player) in weapons for w in
                                      PRIMARY_GUNS]):
                # TODO: add damage instead of 1?
                ranks[i['avg_match_rank']]['dmg'] += 1
        ranks[i['avg_match_rank']]['total'] += 1

    xs = sorted([r for r in ranks], key=lambda x: int(float(x)))
    ys = [ranks[r]['dmg'] / ranks[r]['total'] for r in xs]
    fig = plt.figure()
    plt.plot(xs, ys)
    plt.xticks(xs, xs)
    plt.xlabel("Rank")
    plt.ylabel("Pistol Hit / Round Ratio")
    plt.title("Rank vs Pistol Hit While Having Gun Ratio")
    fig.savefig("pistol_hit_ratio_vs_rank.png")

def nade_dmg_by_rank(rounds):
    pass


if __name__ == "__main__":
    # TODO: add dmg to weapons tuple
    rows = load_data("data/mm_master_demos.csv")
    # generate_headshot_graph(rows)
    rounds = get_rounds(rows)
    # eco_win_percentage(rounds)
    # eco_bomb_plant_percentage(rounds)
    pistol_hits_while_having_gun_by_rank(rounds)
