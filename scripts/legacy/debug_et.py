import pandas as pd
import numpy as np
import os
import math


PATH = r'c:\Users\bruno\fisicambiental\Evapo_2.xlsx'
ALTITUDE_M = 72  # m (altitude de Manaus)
ANO = 2024  # ano real dos dados (INMET)

def pressao_atm_kPa(z_m: float) -> float:
    # Formula FAO-56 para pressão atmosférica padrão em função da altitude
    return 101.3 * ((293 - 0.0065 * z_m) / 293) ** 5.26

P_atm = pressao_atm_kPa(ALTITUDE_M)  # kPa

print(f"Reading file: {PATH}")
try:
    df = pd.read_excel(PATH, sheet_name='Manaus', skiprows=4)
except Exception as e:
    print(f"Error reading excel: {e}")
    exit(1)

rename_map = {
    'DIA': 'dia',
    'TMED (oC)': 'tmed',
    'TMAX (oC)': 'tmax',
    'TMIN (oC)': 'tmin',
    'UR MED (%)': 'ur_med',
    'UR MAX (%)': 'ur_max',
    'UR MIN (%)': 'ur_min',
    'Vento (m/s)': 'vento_med',
    'Vel.Vento Max (m/s)': 'vento_max',
    'Chuva (mm)': 'chuva',
    'Rad. Global (MJ/ma^2)': 'rad_glob',
    'Rad. Líquida (MJ/ma^2)': 'rad_liq',
    'Q_0': 'Ra_extr',
    'es_max': 'es_max',
    'es_min': 'es_min',
    'es': 'es_med',
    'ea': 'ea',
    's': 's_slope'
}
df = df.rename(columns=rename_map)

try:
    df['data'] = pd.to_datetime(df['dia'], format='%d/%m/%Y', errors='coerce')
    
    if df['data'].notna().sum() > len(df) * 0.5:
        print("Formato de data DD/MM/AAAA detectado")
        df['mes'] = df['data'].dt.month
        df['dia_num'] = df['data'].dt.day
        df['julia'] = df['data'].dt.dayofyear
    else:
        raise ValueError("Formato DD/MM/AAAA não detectado, tentando outras opções")
        
except (ValueError, TypeError):
    is_doy = pd.to_numeric(df['dia'], errors='coerce').max() > 31

    if is_doy:
        df['dia_num'] = pd.to_numeric(df['dia'], errors='coerce').fillna(1).astype(int)
        df['data'] = pd.to_datetime(f"{ANO}-01-01") + pd.to_timedelta(df['dia_num'] - 1, unit='D')
        df['mes'] = df['data'].dt.month
        df['julia'] = df['data'].dt.dayofyear
    else:
        mes_col = None
        month_names_pattern = r'Jan|Fev|Mar|Abr|Mai|Jun|Jul|Ago|Set|Out|Nov|Dez'
        possible_names = [m.lower() for m in ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']]

        for c in df.columns:
            try:
                if isinstance(c, str) and c.strip().lower() in possible_names:
                    mes_col = c
                    break
            except Exception:
                continue

        if mes_col is None:
            for c in df.columns:
                try:
                    if df[c].astype(str).str.contains(month_names_pattern, case=False, na=False).any():
                        mes_col = c
                        break
                except Exception:
                    continue

        mes_map = {'Jan':1,'Fev':2,'Mar':3,'Abr':4,'Mai':5,'Jun':6,'Jul':7,'Ago':8,'Set':9,'Out':10,'Nov':11,'Dez':12}

        df['mes'] = np.nan
        if mes_col is not None:
            mapped = df[mes_col].astype(str).str.strip().map(lambda x: mes_map.get(x[:3].capitalize(), None) if isinstance(x, str) else None)
            numeric = pd.to_numeric(df[mes_col], errors='coerce')
            df['mes'] = mapped.fillna(numeric)

        if df['mes'].isna().any():
            months = []
            current_month = 1
            prev_day = None
            dia_numeric = pd.to_numeric(df['dia'], errors='coerce').fillna(1).astype(int)
            for d in dia_numeric:
                if prev_day is None:
                    months.append(current_month)
                else:
                    if d < prev_day:
                        current_month += 1
                        if current_month > 12:
                            current_month = 1
                    months.append(current_month)
                prev_day = d
            inferred = pd.Series(months, index=df.index)
            df['mes'] = df['mes'].fillna(inferred)

        df['mes'] = pd.to_numeric(df['mes'], errors='coerce').fillna(1).astype(int).clip(1,12)
        df['dia_num'] = pd.to_numeric(df['dia'], errors='coerce').fillna(1).astype(int)

        df['data'] = pd.to_datetime({'year': ANO, 'month': df['mes'], 'day': df['dia_num']})
        df['julia'] = df['data'].dt.dayofyear

numeric_cols = df.select_dtypes(include=['float','int']).columns
df[numeric_cols] = df[numeric_cols].interpolate(method='linear')

if 'rad_liq' in df.columns and 'rad_glob' in df.columns:
    ratio = (df['rad_liq'] / df['rad_glob']).describe()
    rad_liq_is_rn = ratio['mean'] < 1.0
else:
    rad_liq_is_rn = False

def esat(T):
    return 0.6108 * np.exp((17.27 * T) / (T + 237.3))  # kPa

if 'es_max' not in df.columns or df['es_max'].isna().all():
    df['es_max'] = esat(df['tmax'])
if 'es_min' not in df.columns or df['es_min'].isna().all():
    df['es_min'] = esat(df['tmin'])
if 'es_med' not in df.columns or df['es_med'].isna().all():
    df['es_med'] = (df['es_max'] + df['es_min']) / 2
if 'ea' not in df.columns or df['ea'].isna().all():
    if 'ur_med' in df.columns:
        df['ea'] = df['es_med'] * df['ur_med'] / 100
    else:
        df['ea'] = df['es_med'] * 0.7

if 's_slope' not in df.columns or df['s_slope'].isna().all():
    df['s_slope'] = 4098 * (0.6108 * np.exp((17.27 * df['tmed']) / (df['tmed'] + 237.3))) / (df['tmed'] + 237.3) ** 2

# Psychrometric constant γ (kPa/°C)
gamma = 0.000665 * P_atm

print('Pressão atmosférica padrão (kPa):', round(P_atm,3))
print('Radiação líquida já considerada Rn?:', rad_liq_is_rn)
print('Linhas e colunas após limpeza:', df.shape)


LAT_GRAUS = -3.1019  # 3°6'7" S em graus decimais negativo (Manaus)
ALBEDO = 0.23
ALPHA_PT = 1.26
G_DIARIO = 0.0  # MJ m-2 d-1 (fluxo de calor no solo diário)

RAD2DEG = 180/np.pi
DEG2RAD = np.pi/180

def ra_extraterrestre(juliano: int, lat_rad: float) -> float:
    # Ra (MJ m-2 d-1) FAO-56 eq. 21
    dr = 1 + 0.033 * np.cos(2 * np.pi / 365 * juliano)
    delta = 0.409 * np.sin(2 * np.pi / 365 * juliano - 1.39)
    ws = np.arccos(-np.tan(lat_rad) * np.tan(delta))
    Ra = (24 * 60 / np.pi) * 0.0820 * dr * (ws * np.sin(lat_rad) * np.sin(delta) + np.cos(lat_rad) * np.cos(delta) * np.sin(ws))
    return Ra

def rso_clear_sky(Ra: float, z_m: float) -> float:
    # Rso (MJ m-2 d-1) FAO-56 eq. 37 (z < 1000 m)
    return (0.75 + 2e-5 * z_m) * Ra

def net_longwave(Rs: float, Rso: float, tmax: float, tmin: float, ea: float) -> float:
    # Rnl (MJ m-2 d-1) FAO-56 eq. 39
    tmaxK = tmax + 273.16
    tminK = tmin + 273.16
    sigma = 4.903e-9  # MJ K-4 m-2 d-1
    term_temp = (tmaxK**4 + tminK**4) / 2
    term_cloud = 1.35 * (Rs / Rso) - 0.35 if Rso > 0 else 0
    Rnl = sigma * term_temp * (0.34 - 0.14 * np.sqrt(ea)) * term_cloud
    return Rnl

def penman_monteith(Rn: float, T: float, u2: float, es: float, ea: float, delta: float, gamma: float, G: float = 0.0) -> float:
    # ET0 (mm d-1) FAO-56 eq. 6
    num = 0.408 * delta * (Rn - G) + gamma * (900/(T+273)) * u2 * (es - ea)
    den = delta + gamma * (1 + 0.34 * u2)
    return num / den if den != 0 else np.nan

def priestley_taylor(Rn: float, delta: float, gamma: float, alpha: float = ALPHA_PT, G: float = 0.0) -> float:
    return alpha * (delta / (delta + gamma)) * 0.408 * (Rn - G)

def hargreaves_samani(Tmean: float, Tmax: float, Tmin: float, Ra: float) -> float:
    # Ra em MJ m-2 d-1 conforme eq. HS original
    return 0.0023 * (Tmean + 17.8) * np.sqrt(max(Tmax - Tmin, 0)) * Ra

lat_rad = LAT_GRAUS * DEG2RAD

if 'Ra_extr' not in df.columns or df['Ra_extr'].isna().all():
    df['Ra_extr'] = df['julia'].apply(lambda j: ra_extraterrestre(int(j), lat_rad))

if 'rad_liq' in df.columns and not df['rad_liq'].isna().all():
    ratio_mean = (df['rad_liq']/df['rad_glob']).replace([np.inf,-np.inf], np.nan).mean()
    usar_rad_liq = ratio_mean < 1.2
else:
    usar_rad_liq = False

print(f"Usar rad_liq: {usar_rad_liq}")

Rn_list = []
for i, row in df.iterrows():
    Rs = row.get('rad_glob', np.nan)
    tmax = row.get('tmax', np.nan)
    tmin = row.get('tmin', np.nan)
    ea = row.get('ea', np.nan)
    Ra = row.get('Ra_extr', np.nan)
    if usar_rad_liq:
        Rn = row.get('rad_liq', np.nan)
    else:
        Rns = (1 - ALBEDO) * Rs
        Rso = rso_clear_sky(Ra, ALTITUDE_M)
        Rnl = net_longwave(Rs, Rso, tmax, tmin, ea)
        Rn = Rns - Rnl
    Rn_list.append(Rn)

df['Rn'] = Rn_list

print(f"NaNs in Rn: {df['Rn'].isna().sum()}")
if df['Rn'].isna().any():
    print("Rows with NaN Rn:")
    print(df[df['Rn'].isna()][['dia', 'rad_glob', 'rad_liq', 'tmax', 'tmin', 'ea', 'Ra_extr']])

if 's_slope' in df.columns:
    delta_col = df['s_slope']
else:
    delta_col = 4098 * (0.6108 * np.exp((17.27 * df['tmed']) / (df['tmed'] + 237.3))) / (df['tmed'] + 237.3) ** 2

u2 = df.get('vento_med', pd.Series(np.full(len(df), 2.0)))

ET_PM = []
ET_PT = []
ET_HS = []

print("Checking inputs for PM/PT...")
print(f"NaNs in tmed: {df['tmed'].isna().sum()}")
print(f"NaNs in es_med: {df['es_med'].isna().sum()}")
print(f"NaNs in ea: {df['ea'].isna().sum()}")
print(f"NaNs in s_slope (delta): {delta_col.isna().sum()}")
print(f"NaNs in vento_med (u2): {u2.isna().sum()}")

for i, row in df.iterrows():
    Rn = row['Rn']
    T = row['tmed']
    es = row['es_med']
    ea = row['ea']
    delta = delta_col.iloc[i]
    wind = u2.iloc[i]
    Ra = row['Ra_extr']
    et_pm = penman_monteith(Rn, T, wind, es, ea, delta, gamma, G_DIARIO)
    et_pt = priestley_taylor(Rn, delta, gamma, ALPHA_PT, G_DIARIO)
    et_hs = hargreaves_samani(T, row['tmax'], row['tmin'], Ra)
    ET_PM.append(et_pm)
    ET_PT.append(et_pt)
    ET_HS.append(et_hs)

df['ET_PM'] = ET_PM
df['ET_PT'] = ET_PT
df['ET_HS'] = ET_HS

print('Resumo ET (mm/d):')
print(df[['ET_PM','ET_PT','ET_HS']].describe())
print(f"NaNs in ET_PM: {df['ET_PM'].isna().sum()}")
print(f"NaNs in ET_PT: {df['ET_PT'].isna().sum()}")
