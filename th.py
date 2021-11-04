from pyvista import examples

dataset = examples.load_uniform()
dataset.set_active_scalars("Spatial Point Data")

# Apply a threshold over a data range
threshed = dataset.threshold([100, 500])

outline = dataset.outline()
dataset.threshold(value=0.05,  all_scalars=True)

print(dataset)