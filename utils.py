from Bio import SeqIO
import pandas as pd
import numpy as np

# -------------------------------
# FASTA PARSER
# -------------------------------
def parse_fasta(uploaded_file):
    sequences = []

    for record in SeqIO.parse(uploaded_file, "fasta"):
        sequences.append({
            "id": record.id,
            "sequence": str(record.seq)
        })

    return pd.DataFrame(sequences)


# -------------------------------
# MUTATION SCAN
# -------------------------------
def mutation_analysis(df):

    reference = df.iloc[0]["sequence"]
    results = []

    for i in range(len(reference)):
        ref_aa = reference[i]
        mutations = 0

        for seq in df["sequence"]:
            if i < len(seq) and seq[i] != ref_aa:
                mutations += 1

        freq = mutations / len(df)

        results.append({
            "Position": i + 1,
            "Reference": ref_aa,
            "Mutation_Frequency": freq
        })

    return pd.DataFrame(results)


# -------------------------------
# EPITOPE PREDICTION (9-mer)
# -------------------------------
def predict_epitopes(sequence, window=9):

    epitopes = []

    for i in range(len(sequence) - window + 1):
        peptide = sequence[i:i+window]

        # Simple antigenicity proxy score
        hydrophobic = sum(aa in "AILMFWYV" for aa in peptide)
        score = hydrophobic / window

        epitopes.append({
            "Start": i + 1,
            "End": i + window,
            "Peptide": peptide,
            "Epitope_Score": score
        })

    return pd.DataFrame(epitopes)


# -------------------------------
# ESCAPE SCORE
# -------------------------------
def escape_score(mutation_df, epitope_df):

    escape_list = []

    for _, epi in epitope_df.iterrows():

        region = mutation_df[
            (mutation_df["Position"] >= epi["Start"]) &
            (mutation_df["Position"] <= epi["End"])
        ]

        mut_freq = region["Mutation_Frequency"].mean()

        escape = mut_freq * epi["Epitope_Score"]

        escape_list.append({
            "Peptide": epi["Peptide"],
            "Start": epi["Start"],
            "End": epi["End"],
            "Escape_Score": escape
        })

    return pd.DataFrame(escape_list)
