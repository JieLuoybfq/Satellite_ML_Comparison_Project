import numpy as np
import sys
import matplotlib.pyplot as plt
import cmap
from skimage.metrics import structural_similarity as ssim

year_dir = '/home/users/rosealyd/ML_sat_obs/monthly/'

def get_as_X_y(X_vars, y_var, year):
	global year_dir
	year_data = np.load(year_dir + str(year)+ '.npy', allow_pickle = True).item()
	
	xais = []
	yais = []
	print(year_data.keys())
	X_vars.append(y_var)
	
	for var in X_vars:
		temp = []
		for month in year_data[var]:
			test = month.ravel()
			temp.extend(test)
		xais.append(temp)
	print(np.array(xais).shape)
	
	if len(xais) == 6:
		xais = [items for items in zip(xais[0], xais[1], xais[2], xais[3], xais[4], xais[-1]) if True not in np.isnan(list(items))]
	if len(xais) == 7:
		xais = [items for items in zip(xais[0], xais[1], xais[2], xais[3], xais[4], xais[5], xais[-1]) if True not in np.isnan(list(items))]
	if len(xais) == 8:
		xais = [items for items in zip(xais[0], xais[1], xais[2], xais[3], xais[4], xais[5], xais[6], xais[-1]) if True not in np.isnan(list(items))]
	if len(xais) == 9:
		xais = [items for items in zip(xais[0], xais[1], xais[2], xais[3], xais[4], xais[5], xais[6], xais[7], xais[-1]) if True not in np.isnan(list(items))]
	
	xais = np.array(xais)
	
	ys = xais[:, -1]
	xais = xais[:, :-1]
	
	X_vars.pop(-1)
	
	return xais, ys, X_vars, [year_dir + str(year)]


def plot_year(predictor, X_vars, y_var, year, GCM = False, GCM_data = None):
	global year_dir
	import datetime
	if GCM:
		year_data = GCM_data
	else:
		year_data = np.load(year_dir + str(year) + '.npy', allow_pickle = True).item()
	pred_y = np.zeros(year_data[y_var][0].shape)
	ssims = []
	mean_diffs = []
	for month in range(len(year_data['LTS'])):
		date = datetime.date(month = month + 1, year = year, day = 1)
		print(date.strftime('%B'))
		
		for lat_row in range(len(year_data['LTS'][month])):
			for lon_tile in range(len(year_data['LTS'][month][lat_row])):
				xai = []
				for var in X_vars:
					xai.append(year_data[var][month][lat_row][lon_tile])
				if True in np.isnan(xai):
					pred_y[lat_row][lon_tile] = np.nan
				else:
					pred_y[lat_row][lon_tile] = predictor.predict([xai])[0]
		land = np.isnan(pred_y)
		year_data['cf'][month][land] = np.nan
		over = (pred_y > 1.)
		pred_y[over] = 1.
		print(np.nanmean(pred_y), 'predicted mean')
		print(np.nanmean(year_data['cf'][month]), 'actual mean')
		mean_diffs.append(np.nanmean(pred_y) - np.nanmean(year_data['cf'][month]))
		'''plt.subplot(131)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], pred_y, vmin = 0, vmax = 1., cmap = cmap.get_bluemap())
		plt.title('Predicted CF')
		plt.colorbar()
		plt.subplot(132)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], year_data['cf'][month], vmin = 0, vmax = 1, cmap = cmap.get_bluemap())
		plt.title('MODIS Monthly CF')
		plt.colorbar()
		plt.subplot(133)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], pred_y - year_data['cf'][month], vmin = -1, vmax = 1, cmap = cmap.get_cmap())
		plt.colorbar()
		plt.suptitle('{} {}'.format(date.strftime('%B'), date.strftime('%Y')))
		plt.show()'''
		pred_y[np.isnan(pred_y)] = 0.
		year_data['cf'][month][np.isnan(year_data['cf'][month])] = 0.
		similarity = ssim(pred_y, year_data['cf'][month], data_range = 1.)
		ssims.append(similarity)
	return ssims, mean_diffs

def get_single_X_y(X_vars, y_var, year):
	global year_dir
	year_data = np.load(year_dir + str(year)+ '.npy', allow_pickle = True).item()
	features_dict = {}
	
	for lat in year_data['latitudes']:
		for lon in year_data['longitudes']:
			features_dict['{}_{}'.format(lat, lon)] = {'X': [], 'y': []}
	
	
	
	for month in range(len(year_data['sst'])):
		for n_row in range(len(year_data['sst'][month])):
			for n_tile in range(len(year_data['sst'][month][n_row])):
				lat = year_data['latitudes'][n_row]
				lon = year_data['longitudes'][n_tile]
				temp_xai = []
				for feature in X_vars:
					temp_xai.append(year_data[feature][month][n_row][n_tile])
				
				if True not in np.isnan(temp_xai) and True not in np.isnan([year_data[y_var][month][n_row][n_tile]]):
					features_dict['{}_{}'.format(lat, lon)]['X'].append(np.array(temp_xai))
					features_dict['{}_{}'.format(lat, lon)]['y'].append(year_data[y_var][month][n_row][n_tile])
	
	remove = []
	for key in features_dict.keys():
		if len(features_dict[key]['X']) < 10:
			remove.append(key)
	for key in remove:
		del features_dict[key]
	
	return features_dict
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
		


					
		