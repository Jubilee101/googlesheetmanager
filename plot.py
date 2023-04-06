from __future__ import print_function

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import numpy as np
import math
from scipy.stats import gaussian_kde
import matplotlib.ticker as ticker
import gspread
import plotly.io as pio
import plotly.express as px
import colorcet as cc
import time
RQS={"trajectory": (3, 
                    {"model-first": [0], 
                     "product-first": [0], 
                     "unsure":[0]
                     }
                     ), 
     "modularity": (5, {}), 
     "model_type": (10, {"Library/API": [0],
                        "Pre-trained model":[0],
                        "Own basic script": [0],
                        "Self-trained model": [0]}),
     "failsafe" : (12, {}),
     "prediction_processing": (11, {}),
     "model_importance": (13, {}),
     "mutilple_model_dependency": (14, {"No":[0],
                                        "Yes, separate functions":[0],
                                        "Yes, used as alternative":[0],
                                        "Yes, chain of execution": [0],
                                        "Yes, combine predictions": [0]}),
     "pipeline": (15, {"No pipeline": [0],
                       "partial pipeline for data fetch" : [0],
                       "Not automated": [0],
                       "Binded by GUI": [0],
                       "Automated": [0]}),
     "testing": (19, {"No": [0],
                      "System": [0],
                      "Model and sys": [0],
                      "All": [0]}),
     "model_evolution": (20, {"Static": [0],
                              "Dynamic": [0]})
     }
SPREADSHEET_ID = '1fcQR4xhy-J2XH1LOdPm-APfm5B-ulkAfbYoqVL7NhGA'
# SPREADSHEET_ID_2 = '1fcQR4xhy-J2XH1LOdPm-APfm5B-ulkAfbYoqVL7NhGA'
CONTRIBUTION_SHEET_ID = '1vMQYHcVIx4ewd5gXHwVmY5thNCeiwsg8YfXwJ2ri1c4'
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
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{abs(x):g}' if x != 0 else '0'))
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    plt.tight_layout()
    plt.savefig(BASE_DIR + '/density_' + name)
    plt.close()

def plot_two_cat(data, cat, name, threshold=-1):
    data1 = []
    data2 = []
    num1 = 0
    num2 = 0
    num3 = 0
    for i in range(len(data)):
        if cat[i] == 'Products based on personal interest' or cat[i] == 'Research product':
            data1.append(data[i])
            if (cat[i] == 'Products based on personal interest'):
                num1 += 1
            else:
                num2 += 1
        elif cat[i] == 'Final end-user product':
            data2.append(data[i])
            num3+=1
        else:
            print('no match')
            print(cat[i])
    print(len(data1))
    print(len(data2))
    input = np.array(data, dtype=int)
    input1 = np.array(data1, dtype=int)
    input2 = np.array(data2, dtype=int)
    size = len(input)
    if threshold > 0:
        input = input[input < threshold]
        print(name + " get rid of " + str(size - len(input)))
        input1 = input1[input1 < threshold]
        input2 = input2[input2 < threshold]
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
    patch1 = mpatches.Patch(color=colors[1], label='End-user')
    patch2 = mpatches.Patch(color=colors[0], label='Personal interest/Research based')
    # plt.legend(handles=[patch1, patch2],fontsize="14")
    # plt.xticks(fontsize=25)
    # plt.yticks(fontsize=25)
    plt.tight_layout()
    plt.savefig(BASE_DIR + '/density_all_' + name)
    plt.close()
    print('b')
    print(num1)
    print(num2)
    print(num3)
    print('e')

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
        print(len(stars))
        contribs = contribs + clean(ws.col_values(10)[1:])
        codebase = codebase + clean(ws.col_values(11)[1:])
    plot_two_cat(stars, cat, "stars.pdf", 10000)
    plot_two_cat(contribs, cat, "contribs.pdf", 170)
    plot_two_cat(codebase, cat, "codebase.pdf", 1500000)

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
    sheets = gc.open_by_key(SPREADSHEET_ID)
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

def plot_attributes(summary_sheet, col, name, group={}):
    values = summary_sheet.col_values(col)[1:]
    for val in values:
        if val not in group:
            group[val] = [0]
        group[val][0] += 1
    n = len(group)
    colors = plt.cm.gray(np.linspace(0, 1, n))

    fig, ax = plt.subplots(figsize=(7, 1.5))
    left = [0]
    i = 0
    print(name)
    label = 'a'
    bbox = dict(boxstyle="Circle", fc="1")
    arrowprops = dict(
    arrowstyle="->",
    connectionstyle="arc3",
    color='white')
    offset_left = 40
    offset_right = 25
    for cat, count in group.items():
        p = ax.barh([""], count, label=cat, left=left, color=colors[i], edgecolor='black',linestyle='solid',linewidth=0.5)
        # ax.bar_label(p, label_type='center', labels=[('('+label+')')], color='white')
        if i == 0:
            ax.annotate(label, (left[0], 0),xytext=(-1 * offset_left, -8), textcoords='offset points',bbox=bbox, arrowprops=arrowprops, fontsize='30')
        elif i == len(group) - 1:
            ax.annotate(label, (left[0] + count[0], 0),xytext=(offset_right, -8), textcoords='offset points',bbox=bbox, arrowprops=arrowprops, fontsize='30')
        label = chr(ord(label) + 1)
        print(cat)
        left[0] += count[0]
        i+=1
    ax.set_ylim(-0.5, 0.6)
    plt.xticks([])
    plt.yticks([])
    plt.xlim(-5,35)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(BASE_DIR + '/' + name, pad_inches=0,bbox_inches='tight')
    plt.close()

def plot_contribution():
    gc = gspread.oauth()
    sheet = gc.open_by_key(CONTRIBUTION_SHEET_ID)
    sheet_ids = []
    for i in range(1, 31):
        if i == 22:
            continue
        sheet_ids.append("P" + str(i))
    work_sheets = []
    for id in sheet_ids:
        work_sheets.append(sheet.worksheet(id))
    se_se = []
    se_ml = []
    se_unsure = []
    se_other = []

    ml_se = []
    ml_ml = []
    ml_unsure = []
    ml_other = []
    for ws in work_sheets:
        values = ws.get_values()
        se_se.append(int(values[1][2])/int(values[0][0]))
        se_ml.append(int(values[2][2])/int(values[0][0]))
        se_unsure.append(int(values[3][2])/int(values[0][0]))
        se_other.append(int(values[4][2])/int(values[0][0]))

        ml_se.append(int(values[1][1])/int(values[0][0]))
        ml_ml.append(int(values[2][1])/int(values[0][0]))
        ml_unsure.append(int(values[3][1])/int(values[0][0]))
        ml_other.append(int(values[4][1])/int(values[0][0]))
    se_stacks = []
    se_stacks.append(np.array(se_ml, dtype=float))
    se_stacks.append(np.array(se_se, dtype=float))
    se_stacks.append(np.array(se_unsure, dtype=float))
    se_stacks.append(np.array(se_other, dtype=float))
    se_bottom = np.zeros(29)

    ml_stacks = []
    ml_stacks.append(np.array(ml_ml, dtype=float))
    ml_stacks.append(np.array(ml_se, dtype=float))
    ml_stacks.append(np.array(ml_unsure, dtype=float))
    ml_stacks.append(np.array(ml_other, dtype=float))
    ml_bottom = np.zeros(29)

    colors = plt.cm.gray(np.linspace(0, 1, 10))
    fig, ax = plt.subplots()
    color_indexes = [9, 8, 4, 0]
    labels = ['ML','SE','Unsure','Other']

    for i in range(len(se_stacks)):
        ax.bar(sheet_ids, se_stacks[i], label=labels[i], color=colors[color_indexes[i]], bottom=se_bottom, edgecolor='black',linestyle='solid',linewidth=0.5)
        se_bottom += se_stacks[i]
    for i in range(len(ml_stacks)):
        ax.bar(sheet_ids, -1*ml_stacks[i], label='', color=colors[color_indexes[i]], bottom=ml_bottom, edgecolor='black',linestyle='solid',linewidth=0.5)
        ml_bottom -= ml_stacks[i]
    plt.legend( fontsize="10", loc='lower left')
    plt.text(-1.5, 0.1, "Non-ML Contribution", rotation=-90)
    plt.text(-1.5, -0.6, "ML Contribution", rotation=-90)
    ax.set_yticks([1, 0, -1])
    for tick in ax.get_yticklabels():
        tick.set_fontsize(30)
    for tick in ax.get_xticklabels():
        tick.set_fontsize(5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim([-2, 28.6])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: f'{abs(y):g}' if y != 0 else '0'))
    plt.tight_layout()
    plt.savefig(BASE_DIR + '/contributions_stacked.pdf')
    plt.close()
def plot_sankey1():
    gc = gspread.oauth()
    sheet = gc.open_by_key(SPREADSHEET_ID)
    summary_sheet = sheet.worksheet("Summary Table")
    col_pred_proc = summary_sheet.col_values(11)[1:]
    col_fail_safe = summary_sheet.col_values(12)[1:]
    labels = [ "Augment", "Prompt","Automate", "No: retrain", "No: score","Yes", "No: none"]
    label_index = {}
    for i in range(len(labels)):
        label_index[labels[i]] = i
    links = {}
    for i in range(len(col_pred_proc)):
        if (col_fail_safe[i] == 'Unsure'):
            continue
        pair = (label_index[col_pred_proc[i]], label_index[col_fail_safe[i]])
        if pair not in links:
            links[pair] = 0
        links[pair] += 1
    source = []
    target = []
    value = []
    for pair, count in links.items():
        source.append(pair[0])
        target.append(pair[1])
        value.append(count)
    # source = [0] + source[:len(source)-1]
    # target = [3] + target[:len(target)-1]
    # value = [2] + value[:len(value)-1]
    # cmap = np.array(cc.CET_C6)
    # colors = cmap[np.linspace(0, len(cmap) - 1, 5).astype(int)]
    # colors[0] = '#EBB02D'
    # colors_op = []
    # for color in colors:
    #     rgba = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.3,)
    #     rgba_string = 'rgba(' + ','.join(map(str, rgba)) + ')'

    # colors_op.append(rgba_string)
    # colors_op = ['rgba(235,176,45,0.3)', 'rgba(157,186,0,0.3)', 'rgba(37,232,231,0.3)', 'rgba(170,158,255,0.3)', 'rgba(246,53,29,0.3)']
    colors_op = ['rgba(235,176,45,0.3)', 'rgba(235,176,45,0.3)', 'rgba(235,176,45,0.3)', 'rgba(170,158,255,0.3)', 'rgba(246,53,29,0.3)']
    link = dict(source = source, target = target, value = value, color=colors_op)
    # node = dict(label = labels, 
    #             pad = 5, 
    #             thickness = 20,
    #             color='grey')
    node = dict(label = labels, 
                pad = 5, 
                thickness = 2,
                color = 'black')
    print(link)
    data = go.Sankey(link = link, node = node)
    some_name="some_figure.pdf"
    fig=px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    pio.write_image(fig, some_name)
    time.sleep(2)
    fig = go.Figure(data)
    fig.update_layout(margin=dict(l=1.5, r=1.5, t=1.5, b=1.5), width=200, height=200, font_color='black',font_size=12)
    pio.write_image(fig, BASE_DIR + '/sankey_pred_proc_fail_safe.pdf')

def plot_sankey2():
    gc = gspread.oauth()
    sheet = gc.open_by_key(SPREADSHEET_ID)
    summary_sheet = sheet.worksheet("Summary Table")
    col_tra = summary_sheet.col_values(3)[1:]
    col_imp = summary_sheet.col_values(13)[1:]
    labels = ["model-first", "product-first", "unsure", "Core", "Optional", "Significant"]
    label_index = {}
    for i in range(len(labels)):
        label_index[labels[i]] = i
    links = {}
    for i in range(len(col_tra)):
        if col_imp[i] == 'None':
            continue
        pair = (label_index[col_tra[i]], label_index[col_imp[i]])
        if pair not in links:
            links[pair] = 0
        links[pair] += 1
    source = []
    target = []
    value = []
    for pair, count in links.items():
        source.append(pair[0])
        target.append(pair[1])
        value.append(count)
    # source = [0] + source[:len(source)-1]
    # target = [3] + target[:len(target)-1]
    # value = [2] + value[:len(value)-1]
    # cmap = np.array(cc.CET_C6)
    # colors = cmap[np.linspace(0, len(cmap) - 1, 5).astype(int)]
    # colors[0] = '#EBB02D'
    # colors_op = []
    # for color in colors:
    #     rgba = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.3,)
    #     rgba_string = 'rgba(' + ','.join(map(str, rgba)) + ')'

    # colors_op.append(rgba_string)
    # colors_op = ['rgba(235,176,45,0.3)', 'rgba(157,186,0,0.3)', 'rgba(37,232,231,0.3)', 'rgba(170,158,255,0.3)', 'rgba(246,53,29,0.3)']
    colors_op = ['rgba(235,176,45,0.3)', 'rgba(170,158,255,0.3)', 'rgba(170,158,255,0.3)', 'rgba(170,158,255,0.3)', 'rgba(246,53,29,0.3)', 'rgba(246,53,29,0.3)', 'rgba(246,53,29,0.3)']
    link = dict(source = source, target = target, value = value, color=colors_op)
    # node = dict(label = labels, 
    #             pad = 5, 
    #             thickness = 20,
    #             color='grey')
    node = dict(label = labels, 
                pad = 5, 
                thickness = 2,
                color = 'black')
    print(link)
    data = go.Sankey(link = link, node = node)
    some_name="some_figure.pdf"
    fig=px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    pio.write_image(fig, some_name)
    time.sleep(2)
    fig = go.Figure(data)
    fig.update_layout(margin=dict(l=1.5, r=1.5, t=1.5, b=1.5), width=200, height=200, font_color='black',font_size=12)
    pio.write_image(fig, BASE_DIR + '/sankey_trajetory_model_importance.pdf')

def plot_sankey3():
    gc = gspread.oauth()
    sheet = gc.open_by_key(SPREADSHEET_ID)
    summary_sheet = sheet.worksheet("Summary Table")
    col_mod = summary_sheet.col_values(5)[1:]
    col_tra = summary_sheet.col_values(13)[1:]
    labels = ["more modular", "less modular", "Core", "Optional", "Significant"]
    label_index = {}
    for i in range(len(labels)):
        label_index[labels[i]] = i
    links = {}
    for i in range(len(col_mod)):
        if col_tra[i] == 'None':
            continue
        pair = (label_index[col_mod[i]], label_index[col_tra[i]])
        if pair not in links:
            links[pair] = 0
        links[pair] += 1
    source = []
    target = []
    value = []
    for pair, count in links.items():
        source.append(pair[0])
        target.append(pair[1])
        value.append(count)
    link = dict(source = source, target = target, value = value)
    # node = dict(label = labels, 
    #             pad = 5, 
    #             thickness = 20,
    #             color='grey')
    node = dict(label = labels, 
                pad = 5, 
                thickness = 2,
                color = 'black')
    print(link)
    data = go.Sankey(link = link, node = node)
    some_name="some_figure.pdf"
    fig=px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    pio.write_image(fig, some_name)
    time.sleep(2)
    fig = go.Figure(data)
    fig.update_layout(margin=dict(l=1.5, r=1.5, t=1.5, b=1.5), width=400, height=200, font_color='black',font_size=12)
    pio.write_image(fig, BASE_DIR + '/sankey_modular_model_importance.pdf')

def main():
    # plot_score()
    # gc = gspread.oauth()
    # sheet = gc.open_by_key(SPREADSHEET_ID)
    # summary_sheet = sheet.worksheet("Summary Table")
    # plot_contributor_background_stacked(summary_sheet)
    plot_contribution()
    # plot_two_cat_all()
    # for name, (col, group) in RQS.items():
    #     plot_attributes(summary_sheet, col, name+'.pdf', group)
    # # plot_sankey3()
    # plot_sankey1()
    # plot_sankey2()

if __name__ == '__main__':
    main()
