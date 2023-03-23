from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.stats import gaussian_kde
import gspread
RQS={"trajectory": 3, 
     "modularity": 5, 
     "model_type": 10,
     "failsafe" : 12,
     "prediction_processing": 11,
     "model_importance": 13,
     "mutilple_model_dependency": 14,
     "pipeline": 15,
     "testing": 19,
     "model_evolution": 20
     }
SPREADSHEET_ID = '1fcQR4xhy-J2XH1LOdPm-APfm5B-ulkAfbYoqVL7NhGA'
SPREADSHEET_ID_2 = '1fcQR4xhy-J2XH1LOdPm-APfm5B-ulkAfbYoqVL7NhGA'
BASE_DIR = 'plots'
def clean(data):
    output = []
    for i in range(len(data)):
        if data[i].isdigit():
            output.append(data[i])
    return output
def clean_float(data):
    output = []
    for i in range(len(data)):
        num = 0.0
        try:
            num = float(data[i])
            # if (num < 10):
            output.append(num)
        except ValueError:
            print(data[i])
    return output

def plot_hist(data, bin=5, name=None):
    input = np.array(data, dtype=int)
    _, bins, _ = plt.hist(input, bins=bin)
    plt.xticks(bins)
    plt.savefig(BASE_DIR + '/hist_' + name)
    plt.close()

def plot_hist_with_threshold(data, bin=5, threshold=0, name=None):
    input = np.array(data, dtype=int)
    global_max = np.max(input)
    lower_input = input[input < threshold]
    lower_min = np.min(lower_input)
    lower_max = np.max(lower_input)
    bins = np.arange(lower_min, lower_max + 1, (lower_max - lower_min + 1) / bin)
    bins = np.append(bins, global_max)
    hist, bin_edges = np.histogram(input,bins)
    fig,ax = plt.subplots()
    ax.bar(range(len(hist)),hist,width=1,align='center',tick_label=
        ['{} - {}'.format(round(bins[i]),round(bins[i+1])) for i,j in enumerate(hist)])
    for tick in ax.get_xticklabels():
        tick.set_fontsize(5)
    plt.savefig(BASE_DIR + '/hist_' + name)
    plt.close()

def plot_whisker(data, whis, name):
    input = np.array(data, dtype=int)
    plt.boxplot(input, whis=whis)
    plt.savefig(BASE_DIR + '/whis_' + name)
    plt.close()

def plot_density(data, name, type=1):
    input = np.array(data, dtype=int) if type == 1 else np.array(data, dtype=float)
    # plt.hist(input, density=True)
    kde = gaussian_kde(input)
    x = np.linspace(min(input), max(input), 291)
    plt.plot(x, kde(x))
    plt.fill_between(x, kde(x), alpha=0.3, color='blue')
    plt.savefig(BASE_DIR + '/density_' + name)
    plt.close()

def plot_density_log(data, name, type=1):
    input = np.array(data, dtype=int) if type == 1 else np.array(data, dtype=float)
    # plt.hist(input, density=True)
    kde = gaussian_kde(input)
    x = np.linspace(0.1, max(input), 1000)
    fig, ax = plt.subplots()
    ax.semilogx(x, kde(x), base=2, color='grey')
    colors = plt.cm.gray(np.linspace(0, 1, 3))[:2]
    plt.fill_between(x, kde(x), where=x<1, alpha=0.3, color=colors[0])
    plt.fill_between(x, kde(x), where=x>1, alpha=0.3, color=colors[1])
    plt.ylim([0, 0.25])
    plt.xlim([0.15, 14.6])
    plt.savefig(BASE_DIR + '/density_' + name)
    plt.close()

def plot_two_cat(data, cat, name):
    data1 = []
    data2 = []
    for i in range(len(data)):
        if cat[i] == 'Products based on personal interest' or cat[i] == 'Research product':
            data1.append(data[i])
        elif cat[i] == 'Final end-user product':
            data2.append(data[i])
    print(len(data1))
    print(len(data2))
    input = np.array(data, dtype=int)
    input1 = np.array(data1, dtype=int)
    input2 = np.array(data2, dtype=int)
    # plt.hist(input, density=True)
    kde1 = gaussian_kde(input1)
    kde2 = gaussian_kde(input2)
    x1 = np.linspace(min(input), max(input), 1000)
    x2 = np.linspace(min(input), max(input), 1000)
    colors = plt.cm.gray(np.linspace(0, 1, 3))[:2]
    # plt.xscale('log')
    plt.plot(x1, kde1(x1), alpha=0.5,color=colors[0])
    plt.plot(x2, kde2(x2), alpha=0.5,color=colors[0])
    plt.fill_between(x1, kde1(x1), alpha=0.5, color=colors[1])
    plt.fill_between(x2, kde2(x2), alpha=0.5, color=colors[0])
    plt.savefig(BASE_DIR + '/density_all_' + name)
    plt.close()

def plot_two_cat_all():
    gc = gspread.oauth()
    sheet = gc.open_by_key(SPREADSHEET_ID)
    mobile_sheet = sheet.worksheet("Mobile")
    desktop_sheet = sheet.worksheet("Desktop")
    web_sheet = sheet.worksheet("Web")
    work_sheets = [mobile_sheet, desktop_sheet, web_sheet]
    stars = []
    contribs = []
    codebase = []
    cat = []
    for ws in work_sheets:
        cat = cat + ws.col_values(7)[1:]
        stars = stars + clean(ws.col_values(9)[1:])
        contribs = contribs + clean(ws.col_values(10)[1:])
        codebase = codebase + clean(ws.col_values(11)[1:])
    plot_two_cat(stars, cat, "stars.pdf")
    plot_two_cat(contribs, cat, "contribs.pdf")
    plot_two_cat(codebase, cat, "codebase.pdf")

def plot_sheet_1():
    gc = gspread.oauth()
    sheet = gc.open_by_key(SPREADSHEET_ID)
    mobile_sheet = sheet.worksheet("Mobile")
    desktop_sheet = sheet.worksheet("Desktop")
    web_sheet = sheet.worksheet("Web")

    sheets = [mobile_sheet, desktop_sheet, web_sheet]
    stars = []
    names = []
    contribs = []
    codebase = []
    for sheet in sheets:
        names = names + sheet.col_values(3)
        stars = stars + clean(sheet.col_values(9))
        contribs = contribs + clean(sheet.col_values(10))
        codebase = codebase + clean(sheet.col_values(11))
    # plot_hist_with_threshold(stars, 5, 2000, "stars.pdf")
    # plot_hist_with_threshold(contribs, 5, 150, "contribs.pdf")
    # plot_hist_with_threshold(codebase, 5, 400000, "codebase.pdf")
    # plot_whisker(stars, 2, "stars.pdf")
    # plot_whisker(contribs, 2, "contribs.pdf")
    # plot_whisker(codebase, 2, "codebase.pdf")
    plot_density(stars, "stars.pdf")
    plot_density(contribs, "contribs.pdf")
    plot_density(codebase, "codebase.pdf")

def plot_score():
    gc = gspread.oauth()
    sheets = gc.open_by_key(SPREADSHEET_ID_2)
    sheet = sheets.worksheet('Findings')
    score = []
    score = score + clean_float(sheet.row_values(10))
    plot_density_log(score, "score.pdf", 0)

def plot_contributor_background_area(summary_sheet):
    total = np.array(summary_sheet.col_values(4)[1:],dtype=int)
    ml = np.array(summary_sheet.col_values(6)[1:], dtype=int)
    se = np.array(summary_sheet.col_values(7)[1:], dtype=int)
    id = summary_sheet.col_values(1)[1:]
    colors = plt.cm.gray(np.linspace(0, 1, 3))[:2]
    fig,ax = plt.subplots()
    plt.stackplot(id, ml, se, labels=['ML', 'SE'], colors=colors)
    for tick in ax.get_xticklabels():
        tick.set_fontsize(5)
    plt.savefig(BASE_DIR + '/contributors_area.pdf')
    plt.close()

def plot_contributor_background_stacked(summary_sheet):
    total = np.array(summary_sheet.col_values(4)[1:],dtype=int)
    ml = np.array(summary_sheet.col_values(6)[1:], dtype=int)
    se = np.array(summary_sheet.col_values(7)[1:], dtype=int)
    unsure = np.array(summary_sheet.col_values(23)[1:], dtype=int)
    other = np.array(summary_sheet.col_values(24)[1:], dtype=int)
    id = summary_sheet.col_values(1)[1:]
    class Contributor:
        def __init__(self, total, ml, se, unsure, other, id):
            self.total = total
            self.ml = ml
            self.se = se
            self.other = other
            self.unsure = unsure
            self.id = id
    contributors = []
    for i in range(len(total)):
        contributors.append(Contributor(total[i], ml[i], se[i], unsure[i], other[i], id[i]))
    def sorter(item):
        return -1 * item.total
    contributors = sorted(contributors, key=sorter)
    ml = np.array(list(map(lambda obj: obj.ml, contributors)) ,dtype=int)
    se = np.array(list(map(lambda obj: obj.se, contributors)) ,dtype=int)
    unsure = np.array(list(map(lambda obj: obj.unsure, contributors)) ,dtype=int)
    other = np.array(list(map(lambda obj: obj.other, contributors)) ,dtype=int)
    id = list(map(lambda obj: obj.id, contributors)) 

    colors = plt.cm.gray(np.linspace(0, 1, 10))
    fig,ax = plt.subplots()
    bottom = np.zeros(30)
    ax.bar(id, ml, label='ML', color=colors[9], bottom=bottom, edgecolor='black',linestyle='solid',linewidth=0.5)
    bottom += ml
    ax.bar(id, se, label = 'SE', color=colors[8],bottom=bottom, edgecolor='black',linestyle='solid',linewidth=0.5)
    bottom += se
    ax.bar(id, unsure, label = 'Unsure', color=colors[4],bottom=bottom, edgecolor='black',linestyle='solid',linewidth=0.5)
    bottom += unsure
    ax.bar(id, other, label = 'Other', color=colors[0],bottom=bottom, edgecolor='black',linestyle='solid',linewidth=0.5)
    ax.legend(fontsize="17")
    for tick in ax.get_xticklabels():
        tick.set_fontsize(5)
    plt.tight_layout()
    plt.savefig(BASE_DIR + '/contributors_stacked.pdf')
    plt.close()

def plot_contributor_background_scattered(summary_sheet):
    total = np.array(summary_sheet.col_values(4)[1:],dtype=int)
    ml = np.array(summary_sheet.col_values(6)[1:], dtype=int)
    se = np.array(summary_sheet.col_values(7)[1:], dtype=int)
    id = summary_sheet.col_values(1)[1:]
    plt.scatter(ml, se, color='black')
    
    plt.savefig(BASE_DIR + '/contributors_scatter.pdf')
    plt.close()

def plot_attributes(summary_sheet, col, name):
    values = summary_sheet.col_values(col)[1:]
    group = {}
    for val in values:
        if val not in group:
            group[val] = [0]
        group[val][0] += 1
    n = len(group)
    colors = plt.cm.gray(np.linspace(0, 1, n+1))

    fig, ax = plt.subplots(figsize=(7, 1))
    left = [0]
    i = 0
    print(name)
    for cat, count in group.items():
        ax.barh([""], count, label=cat, left=left, color=colors[i])
        print(cat)
        left[0] += count[0]
        i+=1
    # ax.set_ylim(0, 5)
    plt.xticks([])
    plt.yticks([])
    plt.xlim(0,29.5)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(BASE_DIR + '/' + name, pad_inches=0,bbox_inches='tight')
    plt.close()
def main():
    gc = gspread.oauth()
    sheet = gc.open_by_key(SPREADSHEET_ID)
    summary_sheet = sheet.worksheet("Summary Table")
    plot_contributor_background_stacked(summary_sheet)

if __name__ == '__main__':
    main()
