import os
import json
import shutil
import pandas as pd
from glob import glob
from collections import defaultdict, Counter

# Move SVG files
svg_path = "./texty/SVG/"
final_destination = "../impersonal-frontend/public/"
config = "./config.json"
svg_files = glob(svg_path+"*.svg")
for svg_file in svg_files:
    shutil.copy2(svg_file, final_destination)
shutil.copy2(config, final_destination)
print("[✓] Copied SVG files to "+final_destination)

# Transform data files
data_path = "../Data/"
data_files = glob(data_path+"*.jsonl")
frontend_data = {}
frontend_data["base_files"] = []
frontend_data["texts"] = []
label_aggregator = {}
for file in data_files:
    basename = os.path.basename(file)
    basename_noext = basename.split(".jsonl")[0]
    frontend_data["base_files"].append(basename)
    df = pd.read_json(file, lines=True)
    for row in df.iterrows():
        id_ = row[1].get("id")
        text_ = row[1].get("text")
        frontend_data["texts"].append({"id": id_, "text": text_})
        labels_ = row[1].get("label")
        for label in labels_:
            label_start = label[0]
            label_end = label[1]
            label_type = label[2]
            if id_ not in label_aggregator:
                label_aggregator[id_] = {}
            if basename_noext not in label_aggregator[id_]:
                label_aggregator[id_][basename_noext] = []
            label_aggregator[id_][basename_noext].append((label_start, label_end, label_type))

def create_aligned_table(data_dict):
    """Create a table that aligns entries from different classifiers."""
    # Get all document IDs
    document_ids = list(data_dict.keys())
    
    result = []
    
    # Process each document
    for doc_id in document_ids:
        doc_data = data_dict[doc_id]
        classifiers = list(doc_data.keys())
        doc_text = [x for x in frontend_data["texts"] if x["id"] == doc_id][0]["text"]
        
        # Get all unique positions across all classifiers for this document
        all_positions = set()
        for classifier in classifiers:
            for start, end, label in doc_data[classifier]:
                all_positions.add((start, end))
        
        # Sort positions
        all_positions = sorted(all_positions)
        
        # Create rows for each position
        for start, end in all_positions:
            # Extract the text span
            span_text = doc_text[start:end] if 0 <= start < end <= len(doc_text) else ""
            
            row = {
                'document_id': doc_id,
                'start': start,
                'end': end,
                'text': span_text
            }
            
            # Add classifier information
            for classifier in classifiers:
                # Find if there's a match for this position in this classifier
                matches = [label for s, e, label in doc_data[classifier] if s == start and e == end]
                row[f"{classifier}_label"] = matches[0] if matches else None
            
            result.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(result)
    
    # Sort by document_id, start, end
    df = df.sort_values(['document_id', 'start', 'end'])
    
    return df

def generate_label_statistics(data_dict):
    """Generate statistics about label usage across classifiers."""
    # Initialize counters for each classifier
    classifier_counters = defaultdict(Counter)
    
    # Count label occurrences for each classifier
    for doc_id, doc_data in data_dict.items():
        for classifier, entries in doc_data.items():
            for _, _, label in entries:
                classifier_counters[classifier][label] += 1
    
    # Create statistics DataFrame
    stats_data = []
    
    # Get all unique labels across all classifiers
    all_labels = set()
    for counter in classifier_counters.values():
        all_labels.update(counter.keys())
    
    # Sort labels alphabetically for consistency
    all_labels = sorted(all_labels)
    
    # Create rows for each label
    for label in all_labels:
        row = {'label': label}
        
        # Add count for each classifier
        for classifier in classifier_counters.keys():
            row[classifier] = classifier_counters[classifier][label]
            # Also add percentage
            total_labels = sum(classifier_counters[classifier].values())
            if total_labels > 0:
                row[f"{classifier}_pct"] = (classifier_counters[classifier][label] / total_labels) * 100
            else:
                row[f"{classifier}_pct"] = 0.0
        
        stats_data.append(row)
    
    # Add total row
    total_row = {'label': 'TOTAL'}
    for classifier in classifier_counters.keys():
        total_row[classifier] = sum(classifier_counters[classifier].values())
        total_row[f"{classifier}_pct"] = 100.0
    
    stats_data.append(total_row)
    
    # Convert to DataFrame
    stats_df = pd.DataFrame(stats_data)
    
    return stats_df

def generate_per_document_statistics(data_dict):
    """Generate statistics about label usage for each document and classifier."""
    # Initialize data structure for statistics
    stats_data = []
    
    # Get all unique classifiers
    all_classifiers = set()
    for doc_data in data_dict.values():
        all_classifiers.update(doc_data.keys())
    all_classifiers = sorted(all_classifiers)
    
    # Get all unique labels
    all_labels = set()
    for doc_data in data_dict.values():
        for entries in doc_data.values():
            all_labels.update(label for _, _, label in entries)
    all_labels = sorted(all_labels)
    
    # Process each document
    for doc_id, doc_data in data_dict.items():
        # Count label occurrences for each classifier in this document
        classifier_counters = {classifier: Counter() for classifier in all_classifiers}
        
        for classifier, entries in doc_data.items():
            for _, _, label in entries:
                classifier_counters[classifier][label] += 1
        
        # Create rows for each label in this document
        for label in all_labels:
            # Skip if this label doesn't appear in this document
            if all(counter[label] == 0 for counter in classifier_counters.values()):
                continue
                
            row = {
                'document_id': doc_id,
                'label': label
            }
            
            # Add count for each classifier
            for classifier in all_classifiers:
                count = classifier_counters[classifier][label]
                row[f"{classifier}_count"] = count
                
                # Add percentage if the classifier has annotations for this document
                total = sum(classifier_counters[classifier].values())
                if total > 0:
                    row[f"{classifier}_pct"] = (count / total) * 100
                else:
                    row[f"{classifier}_pct"] = 0.0
            
            stats_data.append(row)
        
        # Add a total row for this document
        total_row = {
            'document_id': doc_id,
            'label': 'TOTAL'
        }
        
        for classifier in all_classifiers:
            total_count = sum(classifier_counters[classifier].values())
            total_row[f"{classifier}_count"] = total_count
            total_row[f"{classifier}_pct"] = 100.0 if total_count > 0 else 0.0
        
        stats_data.append(total_row)
    
    # Convert to DataFrame
    stats_df = pd.DataFrame(stats_data)
    
    # Sort by document_id and label
    if not stats_df.empty:
        stats_df = stats_df.sort_values(['document_id', 'label'])
        
        # Move TOTAL rows to the end of each document group
        def custom_sort(label):
            return (0 if label == 'TOTAL' else 1, label)
        
        stats_df['sort_key'] = stats_df['label'].apply(custom_sort)
        stats_df = stats_df.sort_values(['document_id', 'sort_key'])
        stats_df = stats_df.drop('sort_key', axis=1)
    
    return stats_df

df2 = create_aligned_table(label_aggregator)
label_stats = generate_label_statistics(label_aggregator)
frontend_data["stats"] = json.loads(label_stats.to_json(orient="records"))
label_stats2 = generate_per_document_statistics(label_aggregator)
frontend_data["stats_by_doc"] = json.loads(label_stats2.to_json(orient="records"))
json.dump({"data": json.loads(df2.to_json(orient="records"))}, open(final_destination+"span_data.json", "w"))
with open(final_destination+"frontend_data.json", "w") as out:
    out.write(json.dumps(frontend_data))
print("[✓] Wrote frontend data to "+final_destination)