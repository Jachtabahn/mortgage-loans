
# Mortgage-Pooling als ganzzahliges lineares Programm

## Variablen

Pro Mortgage `i` and Pool `j` haben wir eine Variable `x_i_j in {0, 1}`.

|               | Pool | 86 | 90 | 98 | 249 | 435 |
| ------------  |------|----|----|----|-----|-----|
| **Mortgage**  |  -   |  - |  - | -  |  -  | -   |
| 1             | -    | 0  | 0  | 0  |  0  |  0  |
| 2             | -    | 0  | 0  | 0  |  0  |  0  |
| 3             | -    | 0  | 0  | 0  |  0  |  0  |


## Konstanten

Wir haben zwei Listen von IDs:
```
mortgages
pools
```

Pro Mortgage `i` haben wir die Konstanten
```
amount_i in R,
fico_i in R,
dti_i in R,
expensive_i in {0, 1},
california_i in {0, 1},
cashout_i in {0, 1},
primary_i in {0, 1},
allowed_pools_i,
prices_i.
```

`allowed_pools_i` ist eine Liste von Pool IDs und `prices_i` eine Liste von reellen Zahlen.

Pro Pool `j` haben wir die Konstanten
```
balance_j in {standard, high},
issuer_j in {single, multi},
servicer_j in {retained, pingora, two_harbors}.
```

Zusätzlich haben wir die Konstanten
```
c_1 in [0, 1],
c_2 in R,
c_3 in R,
c_4 in [0, 1],
c_5 in R,
c_6 in [0, 100],
c_7 in [0, 1],
c_8 in R,
c_9 in R,
c_10 in [0, 100],
c_11 in [0, 1],
c_12 in [0, 1].
```

Ein `x` ist zulässig, wenn es die folgenden Einschränkungen erfüllt:

```
FOR i in mortgages:
    num_chosen := 0
    FOR j in allowed_pools_i:
        num_chosen += x_i_j
    num_chosen == 1
```

```
FOR j in pools:
    sum_j := x_1_j * amount_1 + x_2_j * amount_2 + x_3_j * amount_3
    IF sum_j == 0 THEN CONTINUE

    IF issuer_j == single THEN
        sum_j >= c_2

    weight_1_j := x_1_j * amount_1 / sum_j
    weight_2_j := x_2_j * amount_2 / sum_j
    weight_3_j := x_3_j * amount_3 / sum_j

    rel_num_expensive_j := expensive_1 * weight_1_j + expensive_2 * weight_2_j + expensive_3 * weight_3_j

    IF balance_j == standard THEN
        rel_num_expensive_j <= c_1

    rel_fico_j := fico_1 * weight_1_j + fico_2 * weight_2_j + fico_3 * weight_3_j
    rel_dti_j := dti_1 * weight_1_j + dti_2 * weight_2_j + dti_3 * weight_3_j

    IF servicer_j == pingora THEN
        sum_j <= c_3
        rel_num_expensive_j <= c_4
        rel_fico_j >= c_5
        rel_dti_j <= c_6

        avg_california_j := california_1 * x_1_j + california_2 * x_2_j + california_3 * x_3_j
        avg_california_j <= c_7
    ELSE IF servicer_j == two_harbors THEN
        sum_j >= c_8
        rel_fico_j >= c_9
        rel_dti_j <= c_10

        avg_cashout_j := cashout_1 * weight_1_j + cashout_2 * weight_2_j + cashout_3 * weight_3_j
        avg_cashout_j <= c_11

        avg_primary_j := primary_1 * weight_1_j + primary_2 * weight_2_j + primary_3 * weight_3_j
        avg_primary_j >= c_12
```

Ein `x` hat den Nutzwert `price`, der gegeben ist durch:

```
price := 0
FOR i in mortgages:
    FOR j, p in zip(allowed_pools_i, prices_i):
        price += x_i_j * p
```

Unter Einhaltung der obigen Bedingungen an `x`, wollen wir den Nutzwert `price` von `x` maximieren.


# Alternative Betrachtung

Eine Konfiguration ist gegeben durch die drei Vektoren `features`, `sums`, `counts` mit je 927 reellwertigen Komponenten. Zusätzliche Vereinfachungen gelten:

* Einige Komponenten von `features` haben nur Werte zwischen 0 und 1
* `sums` hat genau 463 Komponenten, die ungleich 0 sein können
* `counts` hat genau 3 Komponenten, die ungleich 0 sein können

Die Dimension der Vektoren wird wiefolgt zerlegt:
```
927 = 458 * 2 + 5 + 5 + 1
```
Die ersten 458 * 2 Komponenten decken die zwei Ungleichungen pro Pool ab. Zehn weitere Komponenten decken die fünf Ungleichungen für Pingora und fünf Ungleichungen für Two Harbors ab. Schließlich gibt es eine Komponente für den zu maximierenden Verkaufswert.

Jedes Haus hat einen reellwertigen Skalar `amount` und eine Menge von Vektoren `translation_j` mit 927 Komponenten. Jedes `translation_j` hat 927 reelle Komponenten.

Eine `translation_j`, zusammen mit `amount` und der aktuellen Konfiguration `features`, `sums`, `counts`, bringt hervor eine neue Konfiguration `features'`, `sums'`, `counts'`. Hierbei werden nur Multiplikationen und Additionen durchgeführt.

Pro Komponente von `features'`:
x' := x * old_sum / (old_sum + amount) + f/(old_sum + amount)
oder
x' := x * 1 + f

Eine zulässige Konfiguration ist eine Konfiguration, wo die ersten 926 Komponenten jeweils 926 vordefinierte Werteschranken beachten. Pro Komponente und Werteschranke, muss die Komponente einen Wert haben, der wie vordefiniert links oder rechts dieser Werteschranke liegt.

Jedes `translation_j` bewegt den Konfigurationsvektor `features` in eine bestimmte Richtung im Raum. Jedes Haus kann diesen Vektor in verschiedene Richtungen bewegen. Die Richtung, in die Haus bewegt wird, kann abhängen von

* der Translation,
* dem `amount` des Hauses,
* den anderen beiden Konfigurationsvektoren `sums` und `counts`.
