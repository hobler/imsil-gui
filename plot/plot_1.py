import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.sparse import eye_array

iter = 1         # iteration (step) to be plotted
smoothie=False   # process surface contour using ploygon from IMSIL distance function
beamplot=False   # plot region of bombardment and toy arrows of beam
paraplot=True    # plot parabolas used to calculate curvature
parab3X3=False
# alpha: after advection
file = open(str(iter)+'/alpha_geometry.txt', 'r')
cols, rows, dx, dy=np.fromfile(file, dtype=int, count=4, sep=" ")
alpha = np.fromfile(file, dtype=float, count=rows*cols, sep=" ").reshape((rows,cols))
# print("alpha["+("%d" %alpha.shape[0])+"]["+("%d" %alpha.shape[1])+"] step "+str(iter))

# U&P: before advection
file = open(str(iter) + '/P.txt', 'r')
P = np.fromfile(file, dtype=float, count=rows * cols, sep=" ").reshape((rows, cols))

df = pd.read_csv(str(iter)+'/U.txt', delimiter=r"\s+", names=["i", "j", "Ux", "Uy", "Uz"])
df["Ux"] = df["Ux"]/dx
df["Uy"] = df["Uy"]/dy
U = df
# print(U)

if smoothie==False: # process contour using contour2d's (Surface(xx) function) result
    df = pd.read_csv(str(iter)+'/contour.txt', delimiter=r"\s+", names=["i", "j", "x1", "y1", "x2", "y2"])
    df["x1"] = df["x1"]/dx+df["i"];
    df["y1"] = df["y1"]/dy+df["j"];
    df["x2"] = df["x2"]/dx+df["i"];
    df["y2"] = df["y2"]/dy+df["j"];
    contour = df.drop(['i', 'j'], axis=1).values
    # print(contour)
else: # process surface contour using ploygon from IMSIL distance function
    contour = []
    counter = -1
    with open('./SURF') as f:
        line = next(f)
        start = True
        for nextline in f:
            skip = False
            if '# Dose' in line:
                counter += 1
                skip = True
            if counter == iter and skip == False and 'E+0' in line:
                firstline = line if(start) else firstline
                start = False
                if '# Dose' not in nextline:
                    x1y1x2y2=(line+" "+nextline).replace('\n', "").split()
                    x1y1x2y2[0] = float(x1y1x2y2[0])/dx+cols/2-0.5
                    x1y1x2y2[1] = -float(x1y1x2y2[1])/dy+rows-0.5
                    x1y1x2y2[2] = float(x1y1x2y2[2])/dx+cols/2-0.5
                    x1y1x2y2[3] = -float(x1y1x2y2[3])/dx+rows-0.5
                    if (x1y1x2y2[0]<=0.5 and x1y1x2y2[2]<=0.5) or (x1y1x2y2[0]>=cols-1.5 and x1y1x2y2[2]>=cols-1.5) \
                            or (int(x1y1x2y2[1])==0 and int(x1y1x2y2[3])==0) or (int(x1y1x2y2[1])==rows-1 and int(x1y1x2y2[3])==rows-1):
                        pass
                    else:
                        contour.append(x1y1x2y2)
                else:
                    pass
            else:
                pass
            line = nextline

# process parabola 2D result
if paraplot==True:
    df = pd.read_csv(str(iter)+'/parabola.txt', delimiter=r"\s+", names=["i", "j", "x", "y", "theta", "a0", "a1", "a2"])
    for index, row in df.iterrows():
        if parab3X3==True:
            x_array = np.linspace(-dx-dx/2, dx+dx/2, 100) # if 3X3 stencil
        else:
            x_array = np.linspace(-dx/2, dx/2, 100) # if only this cell:
        y_array = row["a2"] * x_array**2 + row["a1"] * x_array + row["a0"]
        # local to global rotation
        x_array_rotated = x_array*np.cos(row["theta"])+y_array*np.sin(row["theta"])
        y_array_rotated = -x_array*np.sin(row["theta"])+y_array*np.cos(row["theta"])
        # rotated local to global coordinate of origin
        x_array_global = (x_array_rotated+row["x"])/dx
        y_array_global = (y_array_rotated+row["y"])/dy
        # local rotated moved coordinates to global origin
        if parab3X3 == True:
            mask = (x_array_global>=-1.5)&(x_array_global<=1.5)&(y_array_global>=-1.5)&(y_array_global<=1.5) # if 3X3 stencil
        else:
            mask = (x_array_global>=-1.0)&(x_array_global<=1.0)&(y_array_global>=-1.0)&(y_array_global<=1.0) # if only this cell
        x_array_global = x_array_global[mask]+row["i"]
        y_array_global = y_array_global[mask]+row["j"]
        # if(row["i"]+row["j"]*cols==184): print(row["a0"]); print(row["a1"]); print(row["a2"])
        df["x"] = df["x"].astype(object)
        df["y"] = df["y"].astype(object)
        df.loc[[index], "x"] = pd.Series([x_array_global], index=df.index[[index]])
        df.loc[[index], "y"] = pd.Series([y_array_global], index=df.index[[index]])
    parabola = df.drop(['i', 'j', 'theta', 'a0', 'a1', 'a2'], axis=1).values
    # print(df)
    # print(parabola[184])

# plot heatmap
fig, ax = plt.subplots(figsize=(13, 10), num='Step'+str(iter), layout='constrained')
im = ax.imshow(alpha, cmap='coolwarm')
fig.colorbar(im, orientation='vertical')
# Show all ticks and label them with the respective list entries
width=range(1, cols+1)
height=range(1, rows+1)
ax.set_xticks(np.arange(len(width)), labels=width, fontsize=min(10, 8*50/cols))
ax.set_yticks(np.arange(len(height)), labels=height, fontsize=min(10, 8*50/rows))
plt.xlabel('index i (cell width '+str(dx)+'$\\AA$)', fontsize=10)
plt.ylabel('index j (cell height '+str(dy)+'$\\AA$)', fontsize=10)
# Loop over data dimensions and create text annotations.
xscale=20/max(20, cols)
yscale=20/max(20, rows)
for j in range(len(height)):
    for i in range(len(width)):
        text = ax.text(i, j, str(int(i) + int(j) * cols) + "\n", ha="center", va="center", color="w", fontsize=min(7, 14*xscale*yscale))
        text = ax.text(i, j, "\n\n" + str(alpha[j, i]), ha="center", va="center", color="w", fontsize=min(5, 10*xscale*yscale))
        text = ax.text(i, j, "\n\n\n\n" + str(round(P[j, i] / pow(10, 6))) + " MPa", ha="center", va="center", color="w", fontsize=min(5, 10*xscale*yscale))

# plot U vectors
# max = 0 if max(U["Ux"])<1e-6 else max(U["Ux"]);
ax.quiver((U["i"]+0.5).values, U["j"].values, U["Ux"].values, 0*U["Uy"].values, color='w', alpha=0.3, scale=max(U["Ux"])/(0.02*xscale*yscale))
ax.quiver(U["i"].values, (U["j"]+0.5).values, 0*U["Ux"].values, U["Uy"].values, color='w', alpha=0.3, scale=max(U["Uy"])/(0.02*xscale*yscale))

# plot overlay contour
for cut in contour:
    # print(cut[0], cut[1], cut[2], cut[3])
    ax.plot([cut[0], cut[2]], [cut[1], cut[3]], marker=".", c='black', zorder=10, alpha=0.3)

# plot fitting parabola
if paraplot==True:
    for p in parabola:
        # print(cut[0], cut[1], cut[2], cut[3])
        ax.plot(p[0], p[1], c='black', linestyle='dashed', zorder=10, alpha=0.5)

# plot region of bombardment and toy arrows of beam
if beamplot==True:
    with open('./INP') as f:
        for line in f:
            if 'xwin' in line:
                words = line.replace('=', " ").replace(',', " ").split()
                for i, word in enumerate(words):
                    if word=='xwin':
                        l_range=words[i+1]
                        r_range=words[i+2]
                        break
                break
    l_range=float(l_range)/dx+cols/2-0.5
    r_range=float(r_range)/dx+cols/2-0.5
    x=np.arange(l_range, r_range, 0.01)
    ytop=0*x+rows+1.5
    ybottom=0*x+rows-0.5
    ax.fill_between(x, ytop, ybottom, color="grey", alpha=0.3)
    for i in np.linspace(0, 10, 10):
        ax.arrow(l_range+0+i*(r_range-l_range)/10, rows+1.5, 0, -1.5, head_width=0.25, head_length=0.3)

# alpha: after advection, U&P: before advection
ax.set_title("Step"+str(iter)+": alpha & U & P")
ax.invert_yaxis()
plt.show()