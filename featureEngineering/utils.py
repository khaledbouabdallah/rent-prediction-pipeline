
import math
      
# Inverse Distance Weighting
def inverse_distance_weighting(distances, k):
    return [1 / (d ** k) for d in distances]

# Gaussian Distance Weighting
def gaussian_distance_weighting(distances, sigma):
    return [math.exp(-((d ** 2) / (2 * sigma ** 2))) for d in distances]

# Logarithmic Distance Weighting
def logarithmic_distance_weighting(distances, base):
    return [math.log(1 + (base - d)) for d in distances]

# Linear Distance Weighting
def linear_distance_weighting(distances, max_distance):
    return [max(0, max_distance - d) for d in distances]