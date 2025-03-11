import xarray as xr
import pandas as pd


# This script was created with the following library verions
# xarray v. 2023.1.0
# pandas v. 1.5.2

# * indicates optional components

# load file which has datetime, lat, lon, event*
AMS = pd.read_table('AMS_5species_noscaling.tab', sep='\t', skiprows=51) # open file, tab example
AMS = pd.DataFrame(AMS) # set as pandas df

# rename cols*
AMS.rename(columns={'Date/Time':'Datetime', '[SO4]2- [µg/m**3]':'SO4','[NO3]- [µg/m**3]':'NO3','[NH4]+ [µg/m**3]':'NH4','Cl- [µg/m**3]':'Cl','Org aerosol [µg/m**3]':'OrgAerosol', 'Flag pollution':'Flag', 'QF [NH4]+':'FlagQualityNH4'}, inplace=True)

# set datetime variable format and tz
AMS['Datetime'] = pd.to_datetime(AMS.Datetime, utc=True)


date_str = AMS['Datetime'].dt.strftime('%Y%m%d').astype(int) # extract date from datetime
time_str = AMS['Datetime'].dt.hour * 3600 + AMS['Datetime'].dt.minute * 60 + AMS['Datetime'].dt.second # extract time of day from datetime
julian_str = (AMS['Datetime'].dt.tz_convert('UTC') - pd.Timestamp('2000-01-01', tz='UTC')).dt.total_seconds() / (24 * 3600) # create julian time from 2000-01-01
# without UTC conversions
##julian_str = (AMS['Datetime'] - pd.Timestamp('2000-01-01')).dt.total_seconds() / (24 * 3600) 

# retrieve event number*
event_str = AMS['Event'].str.extract(r'/(?P<int>\d+)').astype(int) # define event, should be replaced by whatever regex identifies event #


# create model input file
# in my file, lat and lon have not needed reformatting, but they could be adjusted and added as defined strings if needed
model_input = xr.Dataset(
    data_vars=dict(
        date = (["profs"], date_str.values),
        time = (["profs"], time_str.values),
        lat = (["profs"], AMS.Latitude.values),
        lon = (["profs"], AMS.Longitude.values),
        orbit_num = (["profs"], event_str.values.flatten()),
        julian = (["profs"], julian_str.values),
    ),
)
model_input["date"] = model_input["date"].assign_attrs(units="yyyymmdd", long_name = "date[yyyymmdd]")
model_input["time"] = model_input["time"].assign_attrs(units="s", long_name = "time of day")
model_input["lat"] = model_input["lat"].assign_attrs(standard_name = "longitude", long_name = "sample_longitude_in_decimal_degrees", units = "degrees_east")
model_input["lon"] = model_input["lon"].assign_attrs(standard_name = "latitude", long_name = "sample_latitude_in_decimal_degrees", units = "degrees_north")
model_input["julian"] = model_input["julian"].assign_attrs(long_name = "UTC Time", units = "days since 2000-01-01", calendar = "proleptic_gregorian")


model_input.to_netcdf('AMS_track.nc', format='NETCDF3_64BIT_DATA') # export file to current working directory as ncdf

# code to check that the file was created and formatted successfully
##import netCDF4 as nc
##f = nc.Dataset('MOSAiC_track.nc', 'r')
##f.file_format

