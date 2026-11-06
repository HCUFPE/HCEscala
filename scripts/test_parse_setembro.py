raw_text = """ALEXANDRE PEREIRA DOS SANTOS	3048008	3048008 TE	TE	CLT	40							FE12D		FE12D		FE6		D6		D6		D6		D6		D6		D6				D6		D6		D6	D6			D6	CH6	168
SIMONE MARQUES DA SILVA	2164828	432676 TE	TE	CLT	36							D6		D6		D6		D6		D6		D6				D6		D6		D6		D6		D6		D6				D6		156
GORETE LOURDES RAIMUNDO  	2173683	304855 TE	TE	CLT	36							D6		D6		D6		D6		D6		D6				D6		D6		D6		D6		D6		D6				D6		156
ANA CLAUDIA A. CLEMENTE	2232181	202071 TE	TE	CLT	36							D6		D6		CH6		D6		D6				D6		D6		D6				D6		D6		D6		D6		D6		150
ANA MARIA DA CONCEIÇÃO	2241712	339727 TE	TE	CLT	36							D6		D6		D6		D6		D6		D6				FE12D		FE12D				FE12D		FE12D		FE12D	FE12D			FE12D		156
AMANDA VIEIRA DA SILVA	3433437	994769 TE	TE	CLT	36							D6		D6		D6		D6		D6		D6				D6		D6		D6		D6		D6		D6				D6		156
JOEL INACIO DO NASCIMENTO	2232211	360238 TE	TE	CLT	36								D6		D6				D6		D6		D6		D6		D6		D6		D6		D6		D6				D6		D6	156
MARIA DE FÁTIMA C. DA SILVA	2173775	567272 TE	TE	CLT	36								D6		D6		D6		D6		D6		D6		D6		D6		D6				D6		D6		D6		D6			156
VERA LÚCIA QUEIROZ DE SOUZA	2244744	491560 TE	TE	CLT	40								D6		D6	D6			D6		FE12D		FE12D		FE12D		FE12D		FE12D				D6		D6		D6		D6		D6	168
DANIELE CONCEIÇÃO V. BERNARDO	3319587	418136 TE	TE	CLT	36								D6		D6		D6		D6				D6		D6		D6		D6				D6		D6		D6		D6		D6	156
EVA MARIA DE SOUZA	3507182	302303 TE	TE	CLT	36								D6		D6				D6		D6		D6		D6		D6		D6		D6		D6		D6				D6		D6	156
ALDSON  ALVES MARCELINO	3467618	1397808 TE	TE	CLT	36								D6		D6				D6		D6		D6		D6		D6		D6				D6		D6		D6		D6		D6	156
CLÁUDIA XAVIER A. DA SILVA	1864400	299672 TE	TE	RJU	30							D6			D6	D6		D6			D6				D6		D6			D6			D6			D6			D6			132
ROSÂNGELA LEITE DA S. COSTA	3312362	1526777 TE	TE	CLT	36							D6			D6			D6			D6		D6	D6			D6		D6	D6			D6			D6			D6		D6	156
ANTÔNIO OTÁVIO DE SENA BARROS 	3422267	2101001TE	TE	CLT	36							CH12D		D6					D6		D6		D6			D6			D6					D6	D6		D6	D6		D6	D6	156
CRISTIANE DE CARVALHO REGO BARROS 	3507458	1989978 TE 	TE	CLT	36									D6			D6			D6	D6		D6		D6	D6			D6			D6			D6			D6		D6	D6	156
ANDRÉA CARLA PEREIRA DA SILVA	3139447	648039 TE	TE	CLT	36								D6		D6				D6		D6	D6			D6		D6	D6		D6		D6		D6			D6			D6		156
FERNANDA OLIVEIRA DA SILVA	1507288	668309 TE	TE	CLT	37								D6		D6	D6			D6			D6			D6		D6	D6		D6		D6		D6			D6		D6			156
VALDJANE NOGUEIRA N. NOBRE	2232733	641179 TE	TE	CLT	36							M16	M16	M16	M16				M16	M16	M16	M16	D6		M16	M16	M16	M16	M16			M16	M16	M16	M16	M16	D6		M16	M16	M16	150
JOSEANE MARIA DA SILVA	3250019	648279 TE	TE	CLT	36							AFIN6	AFIN6	AFIN6	AFIN6	AFIN6		AFIN6	AFIN6	AFIN6	AFIN6	AFIN6	AFIN6		AFIN6	AFIN6	AFIN6	AFIN6	AFIN6	AFIN6		AFIN6	AFIN6	AFIN6	AFIN6	AFIN6	AFIN6		AFIN6	AFIN6	AFIN6	156"""

parsed = []
for line in raw_text.strip().split("\n"):
    parts = line.split("\t")
    nome = parts[0].strip()
    mat = parts[1].strip()
    conselho = parts[2].strip()
    cargo = parts[3].strip()
    vinculo = parts[4].strip()
    ch = parts[5].strip()
    # As 30 colunas de dias vão de parts[6] até parts[35] (total de 30 dias em setembro)
    dias_cols = parts[6:36]
    total_horas = parts[36] if len(parts) > 36 else ""
    
    dias_map = {}
    for idx, val in enumerate(dias_cols):
        dia_num = idx + 1
        val_clean = val.strip()
        if val_clean:
            dias_map[dia_num] = val_clean

    parsed.append({
        "nome": nome,
        "matricula": mat,
        "ch": ch,
        "total_horas": total_horas,
        "dias_count": len(dias_map),
        "dias": dias_map
    })

print(f"Total colaboradores parseados: {len(parsed)}")
for p in parsed:
    print(f"{p['matricula']} - {p['nome']} (Plantões: {p['dias_count']} dias | Total h: {p['total_horas']}): {p['dias']}")
