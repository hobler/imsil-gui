#! /usr/bin/env python3
"""
Read various output data of IMSIL.

Usage: 

mainly meant to be called from other modules, but can also be used as a script
       
     python read_output.px <filename>
       
to do best-guess processing with the IMSIL output file <filename>.

Supported functionalities:

* Read the filenames and parameter values defined in a parameter (.par) file
* Read the value of a parameter from an input (.inp) file
* Read a calculated quantity from an output (.out) file
* Read a histogram from a 1D histogram (.his*) file
* Read a histogram from a 2D histogram (.his*2) file
* Read a collision cascade from a trajectory (.tra) file

Note that there are restriction on reading .his*2 files due to the FortranFile 
module.
"""
import os, sys
import numpy as np
from scipy.io import FortranFile


def read_par(fname, key=None):
    """
    Read filenames and values of a parameter specified in a parameter file
    (unless None).
    
    key: name of the parameter
    """

    with open(fname) as f:
        line = f.readline()
        f.seek(0)
    
        if line.strip().startswith('FILE'):
            basenames = []
            params = []
            for line in f:
                if 'FILE:' in line:
                    basename = line.split()[1]
                    basenames.append(basename)
                if key and key + '=' in line:
                    param = line[:-1].split('=')[1]
                    params.append(param)
        else:
            from collections import OrderedDict
            param = OrderedDict()
            parString = f.read()
            if parString.stript().startswith( 'def ' ):
                from types import FunctionType
                fun_code = compile( parString, '<string>', 'exec' )
                get_params = FunctionType( fun_code.co_consts[0], globals(), 'get_params')
                get_params( param )
            else:    
                exec(parString)
            basenames = list(param.keys())
            if key:
                for basename in basenames:
                    params.append(param[basename][key])
            
    if key:
        return basenames, params
    else:
        return basenames


def read_inp(fname, key):
    """
    Read the value of a parameter from an inp file. The value is returned as a 
    string.
    
    key: name of the parameter
    """
    
    params = []
    
    with open(fname) as f:
        string = f.read()
        items = string.split()
        for item in items:
            if item.startswith(key + '='):
                params.append(item.split('=')[1])
    
    return params


def read_out(fname, search_strings, column=1):
    """
    Read output parameter from an out file.
    
    search_strings: tuple of search strings that will be searched for 
                    consecutively. The last search string must be on the line 
                    containing the parameters
    column:         column of the desired value (column=1...first column 
                    containing data)
                    often: column=1...ion, column=2...first target atom
    """
    
    with open(fname) as f:
        for search_string in search_strings:
            while True:
                line = f.readline()
                if search_string in line:
                    break

    value = line.split('|')[column+1]
    try:
        return float(value)
    except ValueError:
        return value
        

def extract_yield(fname, column=1, backward=True):
    """
    Read the backward or forward scattering/sputtering yield from the .out file.
    
    fname:  name of .out file
    column: column in the sputter yield list
            column=1...ion, column=2...first target atom (for atomic ions)
    
    This function is redundant with read_out.
    """

    if backward:
        kind = 'Backscattered'
    else:
        kind = 'Transmitted'

    with open(fname) as f:
        while True:
            line = f.readline()
            if 'Yield moments:' in line:
                break
        while True:
            line = f.readline()
            if kind + ' atoms per ion:' in line:
                break
        while True:
            line = f.readline()
            if 'mean value' in line:
                syield = line.split('|')[column+1]
                break
        while True:
            line = f.readline()
            if '+/-' in line:
                dyield = line.split('|')[column+1]
                break

    return syield, dyield


def extract_lattice(fname):
    """
    Extract lattice vectors and crystal system from the .out file.
    
    fname:  name of .out file
    """

    with open(fname) as f:
        for line in f:
            if 'crystal system' in line:
                items = line.split(',')
                for item in items:
                    param, value = item.split('=')
                    if 'crystal system' in param:
                        crystal_system = value
            elif 'Lattice vector a' in line:
                a = eval(line.split(':')[1])
            elif 'Lattice vector b' in line:
                b = eval(line.split(':')[1])
            elif 'Lattice vector c' in line:
                c = eval(line.split(':')[1])
    
    return crystal_system, a, b, c


def unify_his(x1, y1, x2, y2):
    """
    Define histograms y1 and y2 on the union of x1 and x2.
    
    x1: abscissas of first histogram
    y1: values of first histogram
    x2: abscissas of second histogram
    y2: values of second histogram
    """
    
    eps = 1e-6*max(np.max(x1), np.max(x2))
    #print x1
    x1tmp = x1
    x1tmp[1::2] += eps
    x2tmp = x2
    x2tmp[1::2] += eps
    #print x1
    x_unified = list(set(x1tmp)|set(x2tmp))
    x_unified.sort()
    x_unified = np.array(x_unified)
    y1_unified = np.interp(x_unified, x1tmp, y1)
    y2_unified = np.interp(x_unified, x2tmp, y2)
    #print x_unified
    x_unified[1::2] = x_unified[:-1:2]
    #print x_unified
    return x_unified, y1_unified, y2_unified    


def add_his(x1, y1, x2, y2, fac1=1, fac2=1):
    """
    Add or take the linear combination two histograms with potentially different abscissas. 
    The result is defined on the union of x1 and x2.
    
    x1: abscissas of first histogram
    y1: values of first histogram
    x2: abscissas of second histogram
    y2: values of second histogram
    fac1: factor for y1
    fac2: factor for y2
    """

    x_unified, y1_unified, y2_unified = unify_his(x1, y1, x2, y2)
    return x_unified, fac1*y1_unified + fac2*y2_unified


def merge_boxes(xx, hist, n_merge):
    """
    Merge n_merge boxes each of the histogram (xx, hist) such that the box 
    boundary closest to the origin is maintained.
    
    xx: abscissas of histogram
    hist: values of histogram
    n_merge: number of boxes to be merged
    """
    
    # remove duplicates
    # note: there is one h value less than x values; h[i] is between x[i-1] and 
    #       x[i]
    x = xx[0::2]
    h = hist[1:-1:2]
    
    # search for position closest to the origin and expand arrays such that 
    # there are multiples of n_merge boxes to the left and right of the origin
    n = len(x) - 1
    i = np.argmin(abs(x))
    nadd_left = -i % n_merge
    nadd_right = -(n-i) % n_merge
    x = np.concatenate((x[0]-(np.arange(nadd_left)[::-1]+1)*(x[1]-x[0]), x,
                        x[-1]+(np.arange(nadd_right)+1)*(x[-1]-x[-2])))
    h = np.concatenate((np.zeros(nadd_left), h, np.zeros(nadd_right)))
    
    # merge boxes
    x = x[::n_merge]
    h = np.array([np.mean(h[i:i+n_merge]) for i in range(0,len(h),n_merge)])
    
    # reconstruct his format
    x = np.vstack((x, x)).T.flatten()
    h = np.vstack((h, h)).T.flatten()
    h = np.concatenate(((hist[0],), h, (hist[-1],)))
    
    return x, h
    

def read_his(fname, record=1, column=1, n_merge=1):
    """
    Read a his file
    
    fname:   name of the .his file or file with compatible format
    record:  the record (block) to be read
    column:  the atom species
             column=1...ion, column=2...first target atom etc. (for atomic ions)
    n_merge: Number of boxes to be merged. The box boundary closest to the 
             origin will be maintained.
    """
    
    if not os.path.exists(fname):
        print(fname, 'does not exist.')

    with open(fname) as f:
        for i in range(record):
            while True:
                line = f.readline()
                if line[0] not in '#*':
                    break
            ncolumns, npoints = [int(var) for var in line.split()]
            line = f.readline()
            x = []
            hist = []
            for __ in range(npoints):
                line = f.readline()
                if i != record-1:
                    continue
                items = line.split()
                x.append(float(items[0]))
                hist.append(float(items[column]))
    
    x = np.array(x)
    hist = np.array(hist)
    if n_merge > 1:
        x, hist = merge_boxes(x, hist, n_merge)

    return x, hist


def read_his2(fname, rec=1, atom=1):
    """
    Read a his2 file.
    
    The returned histogram is hist(z,x).
    """
    if not os.path.exists(fname):
        print(fname, 'does not exist.')

    f = FortranFile(fname)
    for _ in range(rec):
        chars = f.read_record(np.dtype('a1'))
        text = chars.tobytes().rstrip()
#        print('Reading record "', text, '"')
        ints = f.read_ints()
        print('ints=', ints)
        if len(ints) == 3:
            nz, nx, na = ints       # new format
        else:
            nz, nx = ints           # old format
            na = 1
        z = f.read_reals()
        x = f.read_reals()
        for __ in range(atom):
            hist = f.read_reals().reshape((nz,nx))
#            hist = np.maximum(hist, 0)
        for __ in range(na-atom):
            f.read_reals()
#        print('Sum = ', np.sum(hist))
    print(x.shape, z.shape, hist.shape)
    return x, z, hist, text.decode('utf-8')


def read_his3(fname, rec=1, atom=1):
    """
    Read a his3 file.
    
    The returned histogram is hist(z,y,x).
    """
    if not os.path.exists(fname):
        print(fname, 'does not exist.')

    f = FortranFile(fname)
    for _ in range(rec):
        chars = f.read_record(np.dtype('a1'))
        text = chars.tostring().rstrip()
#        print('Reading record "', text, '"')
        ints = f.read_ints()
        print('ints=', ints)
        na, nx, ny, nz = ints
        x = f.read_reals()
        y = f.read_reals()
        z = f.read_reals()
        for __ in range(atom):
            hist = f.read_reals().reshape((nz,ny,nx))
        for __ in range(na-atom):
            f.read_reals()
    return x, y, z, hist, text.decode('utf-8')


class CollisionPoint:
    """
    Decomposes a line of the trajectory file into its variables.
    """
    def __init__(self, line):
        items = line.split()
        try:
            self.x = float(items[0])
            self.y = float(items[1])
            self.z = float(items[2])
            self.dirx = float(items[3])
            self.diry = float(items[4])
            self.dirz = float(items[5])
            self.e = float(items[6])
            self.i1 = int(items[7])
            self.ig = int(items[8])
            self.iflag = int(items[9])
        except:
            sys.exit("Ill-formatted line:\n" + '"' + line + '"')


def read_trajectories(f_, casc=1, last_casc=None):
    """
    Read a tra file of one or several cascades and return a list of cascades 
    consisting of lists of trajectories consisting of lists of collision points.
    
    f_:        name or file object of .tra file
    casc:      first cascade to be read 
               (in case f_ is a file object, relative to current position)
    last_casc: last cascade to be read; None means last_casc=casc
               (in case f_ is a file object, relative to current position)
    """
    if isinstance(f_, str):
        fname = f_
        if not os.path.exists(fname):
            print(fname, 'does not exist.')
        f = open(fname)
    else:
        f = f_
        
    if last_casc is None:
        last_casc = casc
    assert last_casc >= casc

    cascades = []
    
    # read first point
    line = f.readline()
    if not line:
        print('End of file reached')
        if isinstance(f_, str):
            f.close()
        return cascades
    point = CollisionPoint(line)
    
    # skip forward to beginning of cascade casc
    for _ in range(casc-1):
        while True:
            line = f.readline()
            if not line:
                print('End of file reached')
                if isinstance(f_, str):
                    f.close()
                return cascades
            point = CollisionPoint(line)
            if point.i1==1 and point.ig==1 and point.iflag==1:
                break

    # read cascades
    for _ in range(casc, last_casc+1):
        cascade = []                    # list of all trajectories
        trajectory_stack = [ [point] ]  # stack of current generation trajectories
        # loop over collision points of one cascade
        while True:
            # get new point
            old_pos = f.tell()
            line = f.readline()
            if not line:
                print('End of file reached')
                cascades.append(cascade)
                if isinstance(f_, str):
                    f.close()
                return cascades
            point = CollisionPoint(line)
            if point.i1==1 and point.ig==1 and point.iflag==1:
                # next cascade reached
                break
            
            if point.ig > len(trajectory_stack):
                # new trajectory
                for __ in range(len(trajectory_stack), point.ig):
                    trajectory_stack.append([])
            
            # append point to trajectory
            trajectory_stack[point.ig-1].append(point)

            if point.iflag in (0, 3, 4, 5):
                # move trajectory from trajectory_stack to cascade
                assert point.ig == len(trajectory_stack), 'Ill-formatted trajectory file.'
                trajectory = trajectory_stack.pop()
                cascade.append(trajectory)
            
            if len(trajectory_stack) > 0:
                trajectory = trajectory_stack[-1]
                if point.i1 < 0 and point.iflag in (3, 4, 5) and len(trajectory) > 0:
                    if trajectory[-1].i1 == - point.i1:
                        # this is a trajectory that has turned virtual; move it from
                        # trajectory_stack to cascade
                        trajectory_stack.pop()
                        #trajectory[-1].iflag = 3
                        cascade.append(trajectory)
                        
            # pop empty trajectories from the end of trajectory stack
            while len(trajectory_stack) > 0:
                trajectory = trajectory_stack[-1]
                if len(trajectory) == 0:
                    trajectory_stack.pop()
                else:
                    break

        cascades.append(cascade)

    if isinstance(f_, str):
        f.close()
    else:
        f.seek(old_pos)
        
    return cascades
    
    
def main():
    if len(sys.argv) == 1 or len(sys.argv) > 4:
        sys.exit('Usage: python ' + __file__ + ' filename [atom] [record]')
        
    filename = sys.argv[1]
    ext = os.path.splitext(filename)[1]
    
    if len(sys.argv) >= 3:
        column = int(sys.argv[2])
        all_columns = False
    else:
        column = 1
        all_columns = True
    
    if len(sys.argv) == 4:
        record = sys.argv[3]
        all_records = False
    else:
        record = 1
        all_records = True
    
    if ext == '.out':
        while True:
            try:
                syield = read_out(filename, ('Yield moments', 'Backscattered', 
                                             'mean'), column)
                dyield = read_out(filename, ('Yield moments', 'Backscattered', 
                                             'mean', '+/-'), column)
#                syield, dyield = extract_yield(filename, column)
                print('element', column, ':  Yield =', syield, '+/-', dyield)
            except IndexError:
                break
            if not all_columns:
                break
            column += 1
    
    elif ext in ('.his', '.hisee', '.hisne', '.hise', 
                 '.hisb', '.hiseb', '.hisab', '.hisaab',
                 '.hist', '.hiset', '.hisat', '.hisaat'):
        record_complete = True
        while True:
            print('record=', record, ', column=', column)
            try:
                z, hist = read_his(filename, record, column)
                plt.plot(z, hist)
                #plt.xscale('log')
                #plt.xscale('log')
                plt.show()
            except:
                if record_complete:
                    record_complete = False
                    column = 0
                    record += 1
                else:
                    break
            if not all_records and record_complete:
                break
            if not all_columns:
                break
            column += 1
                        
    
    elif ext in ('.his2', '.hisee2', '.hisne2', '.hise2', '.his2b', '.hisa2b', '.hisa2t'):
        record_complete = True
        while True:
            print('record=', record, ', column=', column)
            try:
                x, z, hist, text = read_his2(filename, record, column)
                levels = np.array((0.001,0.003,0.01,0.03,0.1,0.3, 0.9)) \
                         * np.max(hist)
                plt.contour(x, -z, hist, levels)
                plt.gca().set_aspect('equal')
                plt.xlabel('lateral [A]')
                plt.ylabel('vertical [A]')
                text = text.split('=')[1]
                text = text.split(',')[column-1]
                plt.title('Atomic number =' + text 
                          + '\n showing 3 decades below %.4g' % np.max(hist))
                plt.show()
            except TypeError:
                if record_complete:
                    record_complete = False
                    column = 0
                    record += 1
                else:
                    break
            if not all_records and record_complete:
                break
            if not all_columns:
                break
            column += 1

    elif ext in ('.his3', '.hisee3', '.hisne3'):
        try:
            from mayavi import mlab
        except ModuleNotFoundError:
            print('Plotting 3D data requires mayavi2 to be installed.')
            raise
        x, y, z, hist, text = read_his3(filename, record, column)    # returns hist(z,y,x)
        hist = hist.transpose((2,1,0))
        if True:
            # remove small values at the edges
            hist_max_xy = np.max(np.max(hist, axis=1), axis=0)
            hist_max_xz = np.max(np.max(hist, axis=2), axis=0)
            hist_max_yz = np.max(np.max(hist, axis=2), axis=1)
            hist_max = np.max(hist_max_xy)
            ixmin = np.where(hist_max_yz > hist_max*1e-5)[0][0]
            ixmax = np.where(hist_max_yz > hist_max*1e-5)[0][-1]
            iymin = np.where(hist_max_xz > hist_max*1e-5)[0][0]
            iymax = np.where(hist_max_xz > hist_max*1e-5)[0][-1]
            izmin = np.where(hist_max_xy > hist_max*1e-5)[0][0]
            izmax = np.where(hist_max_xy > hist_max*1e-5)[0][-1]
            x = x[ixmin:ixmax+1]
            y = y[iymin:iymax+1]
            z = z[izmin:izmax+1]
            print(ixmin,ixmax,iymin,iymax,izmin,izmax)
            hist = hist[ixmin:ixmax+1,iymin:iymax+1,izmin:izmax+1]
        hist_max = np.max(hist)
        hist = np.log10(np.maximum(hist_max/1e5, hist))
        hist_max = np.log10(hist_max)
        x, y, z = np.meshgrid(x, y, z, indexing='ij')
        print(x.shape, y.shape, z.shape, hist.shape)
        inf_indices = np.transpose(np.nonzero(np.isinf(hist)))
        #for inf_index in inf_indices:
        #    print('infinite value at index ', inf_index)
        mlab.contour3d(x, y, z, hist, opacity=0.6,
                       contours=[hist_max-4.5, hist_max-3.5, hist_max-2.5, 
                                 hist_max-1.5, hist_max-0.5]) 
        mlab.outline()
        mlab.axes()
        mlab.title(text, size=1, height=0.9)
        mlab.show()
    
    elif ext == '.tra':
        casc = 1
        plt.figure()
        while True:
            try:
                cascade, = read_trajectories(filename, casc)
            except ValueError:
                break
            while True:
                try:
                    trajectory = cascade.pop()
                except IndexError:
                    break
                else:
                    if len(trajectory) == 0:
                        continue
                    x = [point.x for point in trajectory]
                    z = [point.z for point in trajectory]
                    if trajectory[0].i1 == 1:   # ion
                        color = 'k'
                        extra_color = 'b'
                        zorder = 2
                    elif trajectory[0].i1 == -1:  # virtual ion
                        color = 'gray'
                        extra_color = 'b'
                        zorder = 2
                    elif trajectory[0].i1 > 1:  # recoil
                        color = 'r'
                        extra_color = 'g'
                        zorder = 1
                    else:                       # virtual recoil
                        color = 'y'
                        extra_color = 'g'
                        zorder = -1
                    plt.plot(x, z, color=color, zorder=zorder)
                    last_point = trajectory[-1]
                    if last_point.iflag in (4, 5):
                        plt.plot((x[-1], last_point.x + 10*last_point.dirx), 
                                 (z[-1], last_point.z + 10*last_point.dirz), 
                                 extra_color)
            plt.gca().set_aspect('equal')
            plt.xlabel('lateral [A]')
            plt.ylabel('vertical [A]')
            plt.title('\n Cascade ' + str(casc))
            plt.show()  
            casc += 1
    
    else:
        sys.exit('Unknown file extension: ' + ext)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    main()
