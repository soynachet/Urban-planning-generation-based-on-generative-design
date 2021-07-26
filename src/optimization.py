

def remap_values(zip_lst):
    input_start = 0
    output_start = 0
    output_end = 1
    remap_values_lst = []
    for values in zip_lst:
        input_end = max(values)
        val_tup = []
        for value in values:
            val_tup.append(output_start + ((output_end - output_start) / (input_end - input_start)) * (value - input_start))
        remap_values_lst.append(val_tup)
    return remap_values_lst


def cal_opt_value(mapped_values, weights):
    value = 0.0
    for val, w in zip(mapped_values, weights):
        value += abs(val[1] - val[0]) * w
    return value



class Opt_class:

    def __init__ (self, plot_info_cad, plot_info_param, weights):
        self.plot_info_cad = plot_info_cad
        self.plot_info_param = plot_info_param
        self.weights = weights

    def optimiza(self):
        mapped_values =  remap_values(zip(self.plot_info_cad, self.plot_info_param))
        opt_value = cal_opt_value(mapped_values, self.weights)
        return opt_value
