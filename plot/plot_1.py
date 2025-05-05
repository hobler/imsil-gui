import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.sparse import eye_array
from pathlib import Path
import argparse

def plot_directory(directory=".", iter=None, smoothie=False, beamplot=False, paraplot=True, parab3X3=False):
        """
        Main plotting function that accepts directory path
        Args:
            directory: Path to IMSIL output directory
            iter: Optional iteration number (defaults to directory name)
            smoothie: Process surface contour using polygon from IMSIL distance function
            beamplot: Plot region of bombardment and beam arrows
            paraplot: Plot parabolas used for curvature calculation
            parab3X3: Use 3x3 stencil for parabola calculation
        """
        directory = Path(directory)
        iter = iter if iter is not None else directory.name

        # Read all required files
        with open(directory/'alpha_geometry.txt', 'r') as file:
            cols, rows, dx, dy = np.fromfile(file, dtype=int, count=4, sep=" ")
            alpha = np.fromfile(file, dtype=float, count=rows*cols, sep=" ").reshape((rows,cols))
        
        with open(directory/'P.txt', 'r') as file:
            P = np.fromfile(file, dtype=float, count=rows * cols, sep=" ").reshape((rows, cols))
        
        df = pd.read_csv(directory/'U.txt', delimiter=r"\s+", names=["i", "j", "Ux", "Uy", "Uz"])
        df["Ux"] = df["Ux"]/dx
        df["Uy"] = df["Uy"]/dy
        U = df

        # Process contour
        if not smoothie:
            df = pd.read_csv(directory/'contour.txt', delimiter=r"\s+", names=["i", "j", "x1", "y1", "x2", "y2"])
            df["x1"] = df["x1"]/dx + df["i"]
            df["y1"] = df["y1"]/dy + df["j"]
            df["x2"] = df["x2"]/dx + df["i"]
            df["y2"] = df["y2"]/dy + df["j"]
            contour = df.drop(['i', 'j'], axis=1).values
        else:
            contour = []
            counter = -1
            with open(directory/'SURF') as f:
                line = next(f)
                start = True
                for nextline in f:
                    skip = False
                    if '# Dose' in line:
                        counter += 1
                        skip = True
                    if counter == int(iter) and not skip and 'E+0' in line:
                        firstline = line if start else firstline
                        start = False
                        if '# Dose' not in nextline:
                            x1y1x2y2 = (line+" "+nextline).replace('\n', "").split()
                            x1y1x2y2[0] = float(x1y1x2y2[0])/dx + cols/2 - 0.5
                            x1y1x2y2[1] = -float(x1y1x2y2[1])/dy + rows - 0.5
                            x1y1x2y2[2] = float(x1y1x2y2[2])/dx + cols/2 - 0.5
                            x1y1x2y2[3] = -float(x1y1x2y2[3])/dx + rows - 0.5
                            if not (x1y1x2y2[0] <= 0.5 and x1y1x2y2[2] <= 0.5) or \
                               (x1y1x2y2[0] >= cols-1.5 and x1y1x2y2[2] >= cols-1.5) or \
                               (int(x1y1x2y2[1]) == 0 and int(x1y1x2y2[3]) == 0) or \
                               (int(x1y1x2y2[1]) == rows-1 and int(x1y1x2y2[3]) == rows-1):
                                contour.append(x1y1x2y2)
                    line = nextline

        # Process parabola results
        if paraplot:
            df = pd.read_csv(directory/'parabola.txt', delimiter=r"\s+", 
                            names=["i", "j", "x", "y", "theta", "a0", "a1", "a2"])
            for index, row in df.iterrows():
                x_array = np.linspace(-dx-dx/2, dx+dx/2, 100) if parab3X3 else np.linspace(-dx/2, dx/2, 100)
                y_array = row["a2"] * x_array**2 + row["a1"] * x_array + row["a0"]
                x_array_rotated = x_array*np.cos(row["theta"]) + y_array*np.sin(row["theta"])
                y_array_rotated = -x_array*np.sin(row["theta"]) + y_array*np.cos(row["theta"])
                x_array_global = (x_array_rotated + row["x"])/dx
                y_array_global = (y_array_rotated + row["y"])/dy
                mask = (x_array_global>=-1.5)&(x_array_global<=1.5)&(y_array_global>=-1.5)&(y_array_global<=1.5) if parab3X3 else \
                       (x_array_global>=-1.0)&(x_array_global<=1.0)&(y_array_global>=-1.0)&(y_array_global<=1.0)
                x_array_global = x_array_global[mask] + row["i"]
                y_array_global = y_array_global[mask] + row["j"]
                df.at[index, "x"] = x_array_global
                df.at[index, "y"] = y_array_global
            parabola = df.drop(['i', 'j', 'theta', 'a0', 'a1', 'a2'], axis=1).values

        # Create plot
        fig, ax = plt.subplots(figsize=(13, 10), num=f'Step{iter}', layout='constrained')
        im = ax.imshow(alpha, cmap='coolwarm')
        fig.colorbar(im, orientation='vertical')
        
        # Configure axes
        width = range(1, cols+1)
        height = range(1, rows+1)
        ax.set_xticks(np.arange(len(width)), labels=width, fontsize=min(10, 8*50/cols))
        ax.set_yticks(np.arange(len(height)), labels=height, fontsize=min(10, 8*50/rows))
        plt.xlabel(f'index i (cell width {dx}$\\AA$)', fontsize=10)
        plt.ylabel(f'index j (cell height {dy}$\\AA$)', fontsize=10)
        
        # Add cell annotations
        xscale = 20/max(20, cols)
        yscale = 20/max(20, rows)
        for j in range(len(height)):
            for i in range(len(width)):
                ax.text(i, j, f"{i + j * cols}\n\n{alpha[j, i]}\n\n\n\n{round(P[j, i] / 1e6)} MPa",
                       ha="center", va="center", color="w",
                       fontsize=min(7, 14*xscale*yscale))

        # Plot vectors
        ax.quiver((U["i"]+0.5).values, U["j"].values, U["Ux"].values, 0*U["Uy"].values,
                 color='w', alpha=0.3, scale=max(U["Ux"])/(0.02*xscale*yscale))
        ax.quiver(U["i"].values, (U["j"]+0.5).values, 0*U["Ux"].values, U["Uy"].values,
                 color='w', alpha=0.3, scale=max(U["Uy"])/(0.02*xscale*yscale))

        # Plot contour
        for cut in contour:
            ax.plot([cut[0], cut[2]], [cut[1], cut[3]], marker=".", c='black', zorder=10, alpha=0.3)

        # Plot parabola
        if paraplot:
            for p in parabola:
                ax.plot(p[0], p[1], c='black', linestyle='dashed', zorder=10, alpha=0.5)

        # Plot beam region
        if beamplot:
            with open(directory/'INP') as f:
                for line in f:
                    if 'xwin' in line:
                        words = line.replace('=', " ").replace(',', " ").split()
                        for i, word in enumerate(words):
                            if word == 'xwin':
                                l_range = float(words[i+1])/dx + cols/2 - 0.5
                                r_range = float(words[i+2])/dx + cols/2 - 0.5
                                break
                        break
            x = np.arange(l_range, r_range, 0.01)
            ytop = 0*x + rows + 1.5
            ybottom = 0*x + rows - 0.5
            ax.fill_between(x, ytop, ybottom, color="grey", alpha=0.3)
            for i in np.linspace(0, 10, 10):
                ax.arrow(l_range + i*(r_range-l_range)/10, rows+1.5, 0, -1.5,
                        head_width=0.25, head_length=0.3)

        ax.set_title(f"Step {iter}: alpha & U & P")
        ax.invert_yaxis()
        plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot IMSIL simulation results')
    parser.add_argument('directory', nargs='?', default='.', 
                      help='Directory containing IMSIL output files')
    parser.add_argument('--iter', type=int, help='Override iteration number')
    parser.add_argument('--smoothie', action='store_true', help='Use SURF file for contours')
    parser.add_argument('--beamplot', action='store_true', help='Show beam region')
    parser.add_argument('--paraplot', action='store_false', help='Hide parabolas')
    parser.add_argument('--parab3X3', action='store_true', help='Use 3x3 stencil')
    
    args = parser.parse_args()
    
    plot_directory(
        directory=args.directory,
        iter=args.iter,
        smoothie=args.smoothie,
        beamplot=args.beamplot,
        paraplot=args.paraplot,
        parab3X3=args.parab3X3
    )