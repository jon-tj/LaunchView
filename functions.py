def seconds_to_h_m_s(seconds):
    """
    Converts seconds to hours, minutes and seconds.
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    
    return "%d:%02d:%02d" % (h, m, s)


def decdeg2dms(dd):
    """
    Converts decimal degrees to degrees, minutes and seconds.
    """
    mult = -1 if dd < 0 else 1
    mnt,sec = divmod(abs(dd)*3600, 60)
    deg,mnt = divmod(mnt, 60)
    return mult*deg, mult*mnt, mult*sec


def convert_gps_lat_coords(deg):
    string = str(deg)
    string = string.split(".")
    string = ("").join(string)

    deg = string[0:2]
    min = string[2:4]
    dec_min = string[4:]

    string = f"{deg}°{min}.{dec_min}'"

    return string


def convert_gps_long_coords(deg):
    string = str(deg)
    string = string.split(".")
    string = ("").join(string)

    deg = string[0:1]
    min = string[1:3]
    dec_min = string[3:]

    string = f"{deg}°{min}.{dec_min}'"

    return string


def convert_to_dms(decimal_degrees):
    """
    Converts degrees, minutes and seconds to decimal degrees.
    """

    degrees = int(decimal_degrees)  # Extract the whole number of degrees
    decimal_part = abs(decimal_degrees - degrees)  # Get the decimal part of the degrees
    minutes, seconds = divmod(decimal_part * 60, 60)  # Convert decimal degrees to minutes and seconds

# Construct the DMS format string
    dms = f"{degrees}°{int(minutes)}'{int(seconds)}\""

    return dms