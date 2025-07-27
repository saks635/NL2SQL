'''def format_prompt(question, schema):
    return f"""
### Schema:
{schema}

### Question:
{question}

### SQL:"""

def clean_sql(sql):
    import re
    sql = sql.strip().rstrip(';')
    sql = sql.replace('\n', ' ')
    sql = re.sub(r'\s+', ' ', sql)
    return sql + ";"'''

import re

def format_prompt(question, schema):
    return f"""
### Schema:
{schema}

### Question:
{question}

### SQL:"""

def clean_sql(sql):
    # Remove markdown code block markers
    sql = sql.strip()
    sql = re.sub(r"```sql|```", "", sql, flags=re.IGNORECASE)
    sql = sql.strip().rstrip(";")
    sql = sql.replace("\n", " ")
    sql = re.sub(r"\s+", " ", sql)
    return sql + ";"
