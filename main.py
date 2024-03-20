import requests
from dotenv import load_dotenv
import inquirer
import os
import io
import psycopg2
import json
import time
from functools import reduce


load_dotenv()



def listEnabledToolsPerRepo(db_username,db_password,db_host,db_port):
    conn = psycopg2.connect(
        dbname="accounts",
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port,
    )
    query = f"""
        SELECT "projectId", "editedTools", "disabledTools", "enabled_tools" from "ProjectSettings";
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    projects = []
    for row in rows:
        row_dict = {
            "repo_id": row[0],
            "edited_tools": json.loads(row[1]),
            "disabled_tools": json.loads(row[2]),
            "enabled_tools": json.loads(row[3]),
        }
        projects.append(row_dict)
    conn.close()
    return projects


def fetchLanguagesPerRepo(db_username,db_password,db_host,db_port,repo_id):
    conn = psycopg2.connect(
        dbname="accounts",
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port,
    )
    query = f"""
        SELECT "language" from "ProjectLanguages" where "projectId"=%s;
    """
    cur = conn.cursor()
    cur.execute(query, (repo_id,))
    rows = cur.fetchall()
    languages = []
    for row in rows:
        languages.append(row[0])
    conn.close()
    return languages


def fetchDefaultToolsForRepo(db_username,db_password,db_host,db_port,languages):
    conn = psycopg2.connect(
        dbname="analysis",
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port,
    )
    query = f"""
        select DISTINCT uuid from "algorithm_language" al 
        left join "Algorithm" a ON al.algorithm_id =a.id 
        where a."default" = false and al."language" = ANY(%s)
    """
    cur = conn.cursor()
    cur.execute(query, (languages,))
    rows = cur.fetchall()
    tools = []
    for row in rows:
        tools.append(row[0])
    conn.close()
    return tools


def getActivePatternsForToolAndRepo(db_username,db_password,db_host,db_port, tool_uuid, repo_id):
    conn = psycopg2.connect(
        dbname="analysis",
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port,
    )
    query = """
    select count(*), p."internalId"  from "ProjectPattern" pp 
    left join "Pattern" p on (pp."patternId" = p."id")
    left join "Algorithm" a on (p."algorithmId" = a."id")
    where pp."projectId" = %s and a."uuid" = %s
    group by p."internalId" 
    """
    cur = conn.cursor()
    cur.execute(
        query,
        (
            repo_id,
            tool_uuid,
        ),
    )
    rows = cur.fetchall()
    patterns = []
    for row in rows:
        patterns.append({"count": row[0], "pattern_id": row[1]})
    conn.close()
    return patterns

def accumulate_sums(acc, item):
    pattern_id = item["pattern_id"]
    count = item["count"]
    if pattern_id in acc:
        acc[pattern_id] += count
    else:
        acc[pattern_id] = count
    return acc

def get_env_var(env_var_name, prompt_message):
    env_var = os.getenv(env_var_name)
    if not env_var:
        questions = [inquirer.Text("env_var", message=prompt_message)]
        answers = inquirer.prompt(questions)
        return answers["env_var"]
    return env_var

def main():
    db_host = get_env_var("DB_HOST", "Your Postgres DB Host")
    db_username = get_env_var("DB_USERNAME", "Your Postgres DB Password")
    db_password = get_env_var("DB_PASSWORD", "Your Postgres DB Password")
    db_analysis_name = get_env_var("DB_ANALYSIS_NAME", "Your Postgres Analsyis DB Name")
    db_accounts_name = get_env_var("DB_ACCOUNTS_NAME", "Your Postgres Accounts DB Name")
    db_port = get_env_var("DB_PORT", "Your Postgres DB Port")
    tools_per_repo = listEnabledToolsPerRepo(db_username,db_password,db_host,db_port)
    for tool in tools_per_repo:
        if tool["edited_tools"] == []:
            languages = fetchLanguagesPerRepo(db_username,db_password,db_host,db_port,tool["repo_id"])
            if languages:
                tool["enabled_tools"] = fetchDefaultToolsForRepo(db_username,db_password,db_host,db_port,languages)
    patterns = []
    for row in tools_per_repo:
        for tool in row["enabled_tools"]:
            patterns += getActivePatternsForToolAndRepo(db_username,db_password,db_host,db_port, tool, row["repo_id"])
    sum_counts = reduce(accumulate_sums, patterns, {})
    sorted_sum_counts = sorted(sum_counts.items(), key=lambda item: item[1], reverse=True)
    print(json.dumps(sorted_sum_counts, indent=4))


if __name__ == "__main__":
    main()
