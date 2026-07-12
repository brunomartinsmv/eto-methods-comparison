# Variáveis meteorológicas derivadas

Este documento deriva as grandezas auxiliares calculadas em `scripts/derived_meteo.py` e consumidas por Penman-Monteith, Priestley-Taylor, Makkink, Hargreaves-Samani e outros métodos.

---

## 1. Pressão de vapor de saturação \(e_s(T)\)

### Base física

A relação entre pressão de vapor de saturação e temperatura segue a forma exponencial da equação de Clausius-Clapeyron. A FAO-56 (Allen et al., 1998, eq. 11) adota a aproximação de Magnus para \(0 \le T \le 50\) °C:

$$e_s(T) = 0{,}6108 \exp\!\left(\frac{17{,}27\,T}{T + 237{,}3}\right) \quad [\mathrm{kPa}]$$

### Derivação (esboço)

Partindo da forma logarítmica da Clausius-Clapeyron para pequenas variações de temperatura em torno de 20 °C, obtém-se:

$$\ln\frac{e_s(T)}{e_s(T_0)} \approx \frac{L}{R_v}\left(\frac{1}{T_0} - \frac{1}{T_K}\right)$$

Ajustando coeficientes empíricos para dados de saturação sobre água líquida, a FAO-56 propõe a forma exponencial acima, onde 0,6108 kPa é \(e_s\) a 0 °C e 237,3 °C é o deslocamento empírico.

**Implementação:** `saturation_vapor_pressure_kpa(t_c)`.

---

## 2. Inclinação da curva de saturação \(\Delta\)

### Definição

$$\Delta = \frac{\mathrm{d}e_s}{\mathrm{d}T}$$

### Derivação

Diferenciando \(e_s(T) = 0{,}6108 \exp(17{,}27\,T/(T+237{,}3))\):

$$\frac{\mathrm{d}}{\mathrm{d}T}\left(\frac{17{,}27\,T}{T+237{,}3}\right) = \frac{17{,}27 \cdot 237{,}3}{(T+237{,}3)^2}$$

Logo:

$$\Delta = e_s(T) \cdot \frac{4098}{(T+237{,}3)^2} \quad [\mathrm{kPa\ ^\circ C^{-1}}]$$

**Implementação:** `vapor_pressure_slope_kpa_c(t_c)`.

---

## 3. Pressão atmosférica e constante psicrométrica \(\gamma\)

### Pressão atmosférica em função da altitude

FAO-56 (eq. 7), perfil barométrico padrão:

$$P = 101{,}3\left(\frac{293 - 0{,}0065\,z}{293}\right)^{5{,}26} \quad [\mathrm{kPa}]$$

onde \(z\) é a altitude em metros.

### Constante psicrométrica

$$\gamma = c_p \frac{P}{\varepsilon\,\lambda} \approx 0{,}000665\,P \quad [\mathrm{kPa\ ^\circ C^{-1}}]$$

com \(c_p \approx 1{,}013\) kJ kg⁻¹ °C⁻¹, razão molecular \(\varepsilon = M_w/M_a \approx 0{,}622\) e \(\lambda = 2{,}45\) MJ kg⁻¹.

**Implementação:** `atmospheric_pressure_kpa`, `psychrometric_constant_kpa_c`.

---

## 4. Pressão de vapor atual \(e_a\)

### A partir de umidade relativa média

Quando apenas \(RH_{mean}\) está disponível:

$$e_a = e_s(T_{mean}) \cdot \frac{RH_{mean}}{100}$$

### A partir de umidades mínima e máxima (FAO-56 eq. 14)

$$e_a = \frac{e_s(T_{min})\,RH_{max} + e_s(T_{max})\,RH_{min}}{200}$$

**Implementação:** `actual_vapor_pressure_kpa(df)`.

---

## 5. Radiação extraterrestre \(R_a\)

### Definição

\(R_a\) é a radiação solar de curto prazo no topo da atmosfera, integrada ao longo do dia, em MJ m⁻² d⁻¹.

### Derivação (FAO-56 eq. 21)

O fluxo extraterrestre instantâneo depende do ângulo de declinação solar \(\delta\) e do ângulo horário no pôr do sol \(\omega_s\):

$$\delta = 0{,}409\sin\!\left(\frac{2\pi}{365}J - 1{,}39\right)$$

$$\omega_s = \arccos\!\bigl(-\tan\varphi\,\tan\delta\bigr)$$

com latitude \(\varphi\) e dia do ano \(J\). A distância Terra–Sol varia com:

$$d_r = 1 + 0{,}033\cos\!\left(\frac{2\pi}{365}J\right)$$

Integrando a irradiância extraterrestre ao longo do dia:

$$R_a = \frac{24 \cdot 60}{\pi}\,G_{sc}\,d_r \left[\omega_s\sin\varphi\sin\delta + \cos\varphi\cos\delta\sin\omega_s\right]$$

com constante solar \(G_{sc} = 0{,}0820\) MJ m⁻² min⁻¹.

**Implementação:** `extraterrestrial_radiation_mj_m2_day(day_of_year, latitude_deg)`.

---

## 6. Conversão de vento para 2 m (FAO-56 eq. 47)

### Perfil logarítmico do vento

A velocidade do vento segue um perfil logarítmico em altura \(z\):

$$u(z) = \frac{u_*}{\kappa}\ln\!\left(\frac{z - d}{z_0}\right)$$

Para grama de referência, a FAO-56 fornece o fator de conversão de altura de medição \(z_m\) para 2 m:

$$u_2 = u_{z_m} \cdot \frac{4{,}87}{\ln(67{,}8\,z_m - 5{,}42)}$$

**Implementação:** `wind_speed_at_2m(wind_m_s, measurement_height_m=10.0)`.

---

## 7. Conversão de fluxo de energia em profundidade de água

### Balanço energético

A evapotranspiração em mm d⁻¹ equivale à lâmina de água evaporada quando 1 mm = 1 kg m⁻²:

$$\mathrm{ET_{mm}} = \frac{R_{\mathrm{MJ\ m^{-2}\ d^{-1}}}}{\lambda}, \qquad \lambda = 2{,}45\ \mathrm{MJ\ kg^{-1}}$$

O fator 0,408 em Penman-Monteith é numericamente equivalente a \(1/\lambda\) quando \(\lambda = 2{,}45\):

$$\frac{1}{\lambda} \approx 0{,}408\ \mathrm{mm\ (MJ\ m^{-2})^{-1}}$$

**Implementação:** `scripts/conversions.py` (`LATENT_HEAT_VAPORIZATION_MJ_KG = 2.45`).

---

## 8. Conversão MJ m⁻² d⁻¹ → cal cm⁻² d⁻¹ (método Turc)

O método Turc histórico usa radiação em cal cm⁻² d⁻¹. O pipeline converte:

$$R_{s,\mathrm{cal\ cm^{-2}\ d^{-1}}} = R_{s,\mathrm{MJ\ m^{-2}\ d^{-1}}} \times 23{,}9006$$

**Implementação:** fator `23.9006` em `scripts/eto_methods.py` (`turc`).

---

## Referências

- Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *Crop Evapotranspiration* (FAO-56). FAO Irrigation and Drainage Paper 56.
