import wave
import numpy as np
import matplotlib.pyplot as plt
import math

def get_audio_arrays(filename, normalize=True):
    """
    Reads in an audio file (.wav) and returns a list of 
    channel audio data, with each channel represented by an array.
    
    **assuming bitdepth 16! *** 
    
    Params:
        normalize: scale audio between -1 and 1
        
        
    Returns:
        if normalized, returns [non-normalized, normalized] audio 
        If not normalized, returns non-normalized audio
    """
    
    audio = wave.open(filename, "r")

    # Extract Raw Audio from Wav File
    signal = audio.readframes(-1)
    signal = np.frombuffer(signal, "int16")
    
    #get number of channels and total number of samples 
    num_channels = audio.getnchannels()
    num_samples = int(len(signal)/num_channels)
    
    #create empty channel arrays
    channels = []
    for i in range(num_channels):
        channels.append(np.empty(num_samples))
    
    #add signal data to channel arrays
    for i in range(num_samples):
        for j in range(num_channels):
            channels[j][i] = signal[i*num_channels + j]
    
    #normalize if necessary
    if normalize:
        normed = np.copy(channels)
        for channel in normed:
            channel /= 2**16
        return channels, normed
    else:
        return channels
    
def get_audio_arrays(filename, normalize=True):
    """
    Reads in an audio file (.wav) and returns a list of 
    channel audio data, with each channel represented by an array.
    
    **assuming bitdepth 16! *** 
    
    Params:
        normalize: scale audio between -1 and 1
        
        
    Returns:
        if normalized, returns [non-normalized, normalized] audio 
        If not normalized, returns non-normalized audio
    """
    
    audio = wave.open(filename, "r")

    # Extract Raw Audio from Wav File
    signal = audio.readframes(-1)
    signal = np.frombuffer(signal, "int16")
    
    #get number of channels and total number of samples 
    num_channels = audio.getnchannels()
    num_samples = int(len(signal)/num_channels)
    
    #create empty channel arrays
    channels = []
    for i in range(num_channels):
        channels.append(np.empty(num_samples))
    
    #add signal data to channel arrays
    for i in range(num_samples):
        for j in range(num_channels):
            channels[j][i] = signal[i*num_channels + j]
    
    #normalize if necessary
    if normalize:
        normed = np.copy(channels)
        for channel in normed:
            channel /= 2**16
        return channels, normed
    else:
        return channels
    
    
def get_xvals(chans, sr):
    #create x values 
    seconds = len(chans[0]) / sr
    xvals = np.linspace(0, seconds, num = len(chans[0]))
    
    return xvals 


    
def plot_channels(chans, colors, xvals, sr, xlim, title=None, norm=False):
    """
    Plot given channel arrays in the given colors.
    """
    
    for i in range(len(chans)):
        fig, ax = plt.subplots()
        ax.plot(xvals, chans[i], color=colors[i])
        if norm:
            ax.set_ylim(-1, 1)
        ax.set_xlim(0, xlim)
        ax.set_facecolor("black")
        fig.set_size_inches(18, 2)
        
        
        if title:
            figtitle = title + ": Channel " + str(i)
        else: 
            figtitle = "Channel " + str(i)
        if norm:
            fig.suptitle(figtitle + " (Normalized)")
        else:
            fig.suptitle(figtitle)
        
        
        #plt.axis("off")
        plt.show()
        #fig.savefig(title+str(i)+'.jpg', dpi=300, transparent=False)
    
    

def bin_channels(channels, bin_size, gain, xvals, normalize=False):
    """
    Bin channels according to bin size and multiply by gain.
    Returns binned channels. 
    """
    num_bins = math.ceil(len(channels[0])/bin_size)
    
    binned_channels = []
    binned_xvals = []
    for i in range(len(channels)):
        binned_channels.append(np.empty(num_bins))
        binned_xvals.append(np.empty(num_bins))
    
    for i in range(num_bins):
        for j in range(len(channels)):
            mean = np.mean(channels[j][i*bin_size: (i+1)*bin_size])
            binned_channels[j][i] = mean*gain
            binned_xvals[j][i] = xvals[i*bin_size + np.argmin(np.abs(channels[j][i*bin_size: (i+1)*bin_size] - mean))]
            
    if normalize:
        #normalize each bin
        for i in range(len(channels)):
            min = np.min(binned_channels[i])
            max = np.max(binned_channels[i])
            binned_channels[i] -= min
            binned_channels[i] /= (max - min)*.5
            binned_channels[i] -= 1
            
    return binned_channels, binned_xvals


def plot_binned(binned_chans, bin_size, sr, colors, xvals, xlim, title=None, ylim=1):
    """
    Plot binned channels with points in the middle of their binned intervals.
    """
    num_bins = len(binned_chans[0])
    
    #get xvals
    
    for i in range(len(binned_chans)):
        fig, ax = plt.subplots()
        ax.plot(xvals[i], binned_chans[i], color=colors[i])
        ax.set_ylim(-ylim, ylim)
        ax.set_xlim(0, xlim)
        ax.set_facecolor("black")
        fig.set_size_inches(18, 2)
        
        
        if title:
            fig.suptitle(title + ": Channel " + str(i) + ", Bin Size = " + str(bin_size))
        else:
            fig.suptitle("Channel " + str(i) + ", Bin Size = " + str(bin_size))
        
        #plt.axis("off")
        plt.show()
        #fig.savefig(title + str(i) + '_binned.jpg', dpi=300, transparent=False)
        

        
def get_shapes(binned_data, binned_xvals):
    """
    Turn binned data into shapes, up or down. 
    Attach xvals as time information.
    """
    channel_shapes = []
    for i in range(len(binned_data)):
        channel = binned_data[i]
        shapes = []
        for j in range(len(channel) - 1):
            start = channel[j]
            end = channel[j+1]
            if (end > start):
                shapes.append(["u", binned_xvals[i][j]])
            else:
                shapes.append(['d', binned_xvals[i][j]])
        channel_shapes.append(shapes)
    
    
    return channel_shapes 



def shapes_to_cube_notation(shapes, face):
    """
    Turn one channel of shapes into cube notation. 
    
    Faces:
        L, R, F, B, U, D
        
    Hand:
        L, R
    """
    
    #aggregate into [shape, number-of-repeats]
    i = 0
    aggregated = []
    curr_count = 0
    while(i < len(shapes)-1):
        curr_shape = shapes[i][0]
        curr_count += 1
        next_shape = shapes[i+1][0]
        if (next_shape != curr_shape):
            aggregated.append([shapes[i], curr_count])
            curr_count = 0
        i+=1
    
    #translate repeats by modulo 4:
    #1 -- > shape
    #2 -- > shape2
    #3 -- > opposite shape
    #4 -- > skip 
    translated = []
    for move in aggregated: 
        shape = move[0][0]
        number = move[1] % 4
        if (number == 1):
            translated.append([move[0], 1])
        
        elif (number ==2):
            translated.append([move[0], 2])
        
        elif (number == 3):
            if (shape == 'u'):
                translated.append([['d', move[1]], 1])
            
            else:
                translated.append([['u', move[1]], 1])

                
    #translate into cube notation
    
    notation = []
    for move in translated:
        if (move[1] == 2):
            notation.append([face + "2", move[0][1]])
        else:
            if (move[0][0] == 'u'):
                notate = [face, move[0][1]]
            else:
                notate = [face + "\'", move[0][1]]
            notation.append(notate)
    
    return aggregated, translated, notation

