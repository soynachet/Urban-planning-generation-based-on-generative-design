
def variance(data):
    """determine the variance between a list of axis"""
    # Number of observations
    n = len(data)
    # Mean of the data
    mean = sum(data) / n
    # Square deviations
    deviations = [(x - mean) ** 2 for x in data]
    # Variance
    if n > 1:
        variance = sum(deviations) / (n - 1)
    else:
        variance = 10
    return variance / 10


def remap_values(plot_info_cad, plot_info_param):
    remap_values_end = []
    for info in plot_info_param:
        input_start = 0
        output_start = 1
        output_end = 10
        remap_values_lst = []
        for values in zip(plot_info_cad, info):
            input_end = max(values)
            val_tup = []
            for value in values:
                val_tup.append(output_start + ((output_end - output_start) / (input_end - input_start)) * (value - input_start))
            remap_values_lst.append(val_tup)
        remap_values_end.append(remap_values_lst)
    return remap_values_end


def cal_opt_value(mapped_values, weights, nr_plots):
    variance_lst = [[],[],[],[],[]]
    for sublst in mapped_values:
        for i, val in enumerate(sublst):
            variance_lst[i].append(val[0])
    variance_factor = [variance(data) * w for data, w in zip(variance_lst, weights)]
    value = 0.0
    for sublst in mapped_values:        
        for val, w, f in zip(sublst, weights, variance_factor):
            value += (abs(val[1] - val[0]) ** 3) * (w +  f)
    values_no_zeros = []
    for sublst in mapped_values:
        if 1.0 not in sublst[4]:
            values_no_zeros.append(sublst)
    if len(values_no_zeros) > 0:
        opt_value =  value / len(values_no_zeros)
    else:
        opt_value =  value
    nr_factor = nr_plots - ((len(mapped_values) + len(values_no_zeros)) / 2 ) + 1
    if nr_factor == 1:
        return opt_value
    elif nr_factor > 1:
        return opt_value + opt_value * (nr_factor * weights[-1])


class Opt_class:

    def __init__ (self, plot_info_cad, plot_info_param, cad_reduction, weights, nr_plots):
        self.plot_info_cad = plot_info_cad
        self.plot_info_param = plot_info_param
        self.cad_reduction = cad_reduction
        self.weights = weights
        self.nr_plots = nr_plots

    def optimiza(self):
        plot_info_cad_reduzed = [plot_info * self.cad_reduction for plot_info in self.plot_info_cad]
        mapped_values = remap_values(plot_info_cad_reduzed, self.plot_info_param)
        opt_value = cal_opt_value(mapped_values, self.weights, self.nr_plots)
        return plot_info_cad_reduzed, opt_value
