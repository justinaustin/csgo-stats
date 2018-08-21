import csv
import pprint

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


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


# games = {}
# for i in rows:
#     if i['file'] not in games:
#         # new game
#         games[i['file']] = []
#         last_round_seen = i['round']
#         games.append({
#             'map': i['map'],
#             'date': i['date'],
#             'round': i['round'],
#             'att_team': i['att_team'],
#             'vic_team': i['vic_team'],
#             'att_side' i['att_side'],
#             'vic_side': i['vic_side'],
# })

if __name__ == "__main__":
    rows = load_data("data/mm_master_demos.csv")
    generate_headshot_graph(rows)
