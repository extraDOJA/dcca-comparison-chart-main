import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sagicor Monitoring Demo", layout="wide")

# Skip authentication and render the app directly
st.session_state["authentication_status"] = True


def get_bank_recon_df() -> pd.DataFrame:
    """Demo data for reconciling Sunsystem, Genelco, Capsil to the VEFT bank file."""
    weeks = pd.to_datetime(["2025-12-08", "2025-12-15", "2025-12-22", "2025-12-29"])
    rows = [
        {"week": weeks[0], "system": "Sunsystem", "match_pct": 97.2, "outstanding": 7, "note": "Aging items tied to timing differences."},
        {"week": weeks[1], "system": "Sunsystem", "match_pct": 98.3, "outstanding": 4, "note": "VEFT file late delivery adjusted."},
        {"week": weeks[2], "system": "Sunsystem", "match_pct": 98.9, "outstanding": 3, "note": "Duplicate entries cleared."},
        {"week": weeks[3], "system": "Sunsystem", "match_pct": 99.1, "outstanding": 2, "note": "Residual suspense entries under review."},
        {"week": weeks[0], "system": "Genelco", "match_pct": 95.4, "outstanding": 11, "note": "Legacy policy cash items unmatched."},
        {"week": weeks[1], "system": "Genelco", "match_pct": 96.8, "outstanding": 8, "note": "Mapping corrected for premium reversals."},
        {"week": weeks[2], "system": "Genelco", "match_pct": 97.6, "outstanding": 6, "note": "Waiting VEFT confirmation on two items."},
        {"week": weeks[3], "system": "Genelco", "match_pct": 98.2, "outstanding": 4, "note": "Control log confirms catch-up batch posted."},
        {"week": weeks[0], "system": "Capsil", "match_pct": 93.9, "outstanding": 15, "note": "High volume of benefits adjustments."},
        {"week": weeks[1], "system": "Capsil", "match_pct": 95.5, "outstanding": 10, "note": "ESB replay cleared older suspense lines."},
        {"week": weeks[2], "system": "Capsil", "match_pct": 96.7, "outstanding": 8, "note": "Two-day lag from VEFT file receipt."},
        {"week": weeks[3], "system": "Capsil", "match_pct": 97.4, "outstanding": 6, "note": "Pending validation of refunds."},
    ]
    return pd.DataFrame(rows)


def get_esb_df() -> pd.DataFrame:
    """Demo data for ESB failures and resubmissions to SUN GL."""
    weeks = pd.to_datetime(["2025-12-08", "2025-12-15", "2025-12-22", "2025-12-29"])
    rows = [
        # week, feed, total, failed, resubmitted, open
        {"week": weeks[0], "feed": "BEL", "total": 520, "failed": 6, "resubmitted": 5, "open": 1},
        {"week": weeks[1], "feed": "BEL", "total": 530, "failed": 4, "resubmitted": 4, "open": 0},
        {"week": weeks[2], "feed": "BEL", "total": 525, "failed": 3, "resubmitted": 3, "open": 0},
        {"week": weeks[3], "feed": "BEL", "total": 540, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[0], "feed": "CAB", "total": 430, "failed": 5, "resubmitted": 4, "open": 1},
        {"week": weeks[1], "feed": "CAB", "total": 435, "failed": 4, "resubmitted": 4, "open": 0},
        {"week": weeks[2], "feed": "CAB", "total": 440, "failed": 4, "resubmitted": 3, "open": 1},
        {"week": weeks[3], "feed": "CAB", "total": 450, "failed": 3, "resubmitted": 3, "open": 0},
        {"week": weeks[0], "feed": "SLA", "total": 310, "failed": 4, "resubmitted": 3, "open": 1},
        {"week": weeks[1], "feed": "SLA", "total": 320, "failed": 3, "resubmitted": 3, "open": 0},
        {"week": weeks[2], "feed": "SLA", "total": 318, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[3], "feed": "SLA", "total": 322, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[0], "feed": "SLB", "total": 290, "failed": 3, "resubmitted": 2, "open": 1},
        {"week": weeks[1], "feed": "SLB", "total": 295, "failed": 3, "resubmitted": 3, "open": 0},
        {"week": weeks[2], "feed": "SLB", "total": 292, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[3], "feed": "SLB", "total": 298, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[0], "feed": "SLT", "total": 255, "failed": 3, "resubmitted": 2, "open": 1},
        {"week": weeks[1], "feed": "SLT", "total": 258, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[2], "feed": "SLT", "total": 262, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[3], "feed": "SLT", "total": 265, "failed": 1, "resubmitted": 1, "open": 0},
        {"week": weeks[0], "feed": "SOT", "total": 210, "failed": 4, "resubmitted": 3, "open": 1},
        {"week": weeks[1], "feed": "SOT", "total": 215, "failed": 3, "resubmitted": 3, "open": 0},
        {"week": weeks[2], "feed": "SOT", "total": 220, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[3], "feed": "SOT", "total": 225, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[0], "feed": "SSL", "total": 240, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[1], "feed": "SSL", "total": 245, "failed": 2, "resubmitted": 2, "open": 0},
        {"week": weeks[2], "feed": "SSL", "total": 250, "failed": 1, "resubmitted": 1, "open": 0},
        {"week": weeks[3], "feed": "SSL", "total": 255, "failed": 1, "resubmitted": 1, "open": 0},
    ]
    return pd.DataFrame(rows)


def get_genelco_oversight_df() -> pd.DataFrame:
    """Demo data for weekly oversight of Genelco -> SUN GL."""
    weeks = pd.to_datetime(["2025-12-08", "2025-12-15", "2025-12-22", "2025-12-29"])
    rows = [
        {"week": weeks[0], "feed": "Genelco -> SUN", "success_rate": 98.4, "exceptions": 3, "status": "Stable", "notes": "Three reversals required manual coding."},
        {"week": weeks[1], "feed": "Genelco -> SUN", "success_rate": 99.0, "exceptions": 2, "status": "Improving", "notes": "Control log cleanup post policy migration."},
        {"week": weeks[2], "feed": "Genelco -> SUN", "success_rate": 98.7, "exceptions": 3, "status": "Stable", "notes": "Two suspense items pending client confirmation."},
        {"week": weeks[3], "feed": "Genelco -> SUN", "success_rate": 99.3, "exceptions": 1, "status": "Stable", "notes": "Weekly/monthly reporting ready for Finance review."},
    ]
    return pd.DataFrame(rows)


def get_ifrs17_df() -> pd.DataFrame:
    """Demo data for IFRS17 postings from ESB to SUN GL."""
    rows = [
        {"date": "2025-12-23", "batch_id": "IFRS17-1223-A", "records": 1850, "posted_to_sun": 1846, "status": "Posted", "comment": "Four policies requeued for delta posting."},
        {"date": "2025-12-24", "batch_id": "IFRS17-1224-A", "records": 1920, "posted_to_sun": 1918, "status": "Posted", "comment": "Two valuation lines reviewed by Finance."},
        {"date": "2025-12-26", "batch_id": "IFRS17-1226-A", "records": 2050, "posted_to_sun": 2045, "status": "Posted", "comment": "GL acceptance confirmed; minor rounding noted."},
        {"date": "2025-12-27", "batch_id": "IFRS17-1227-A", "records": 2105, "posted_to_sun": 2101, "status": "Posted", "comment": "ESB latency improved after patch."},
        {"date": "2025-12-29", "batch_id": "IFRS17-1229-A", "records": 2250, "posted_to_sun": 2244, "status": "In Progress", "comment": "Six records under review for account mapping."},
        {"date": "2025-12-30", "batch_id": "IFRS17-1230-A", "records": 2180, "posted_to_sun": 0, "status": "Queued", "comment": "Awaiting Finance sign-off on batch keys."},
    ]
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["posting_pct"] = (df["posted_to_sun"] / df["records"] * 100).round(1)
    return df


if st.session_state["authentication_status"]:
    st.title("Sagicor Monitoring Control Room")
    st.caption("Demo view covering bank reconciliation support, ESB resubmissions, Genelco oversight, and IFRS17 interfacing.")

    bank_df = get_bank_recon_df()
    esb_df = get_esb_df()
    genelco_df = get_genelco_oversight_df()
    ifrs_df = get_ifrs17_df()

    latest_week = esb_df["week"].max()
    latest_bank_week = bank_df["week"].max()

    total_msgs = int(esb_df["total"].sum())
    total_fail = int(esb_df["failed"].sum())
    success_rate = round((1 - total_fail / total_msgs) * 100, 2)
    resubmissions_this_week = int(esb_df.loc[esb_df["week"] == latest_week, "resubmitted"].sum())
    open_failures = int(esb_df.loc[esb_df["week"] == latest_week, "open"].sum())
    bank_outstanding = int(bank_df.loc[bank_df["week"] == latest_bank_week, "outstanding"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall ESB Success Rate", f"{success_rate}%", "Across BEL, CAB, SLA, SLB, SLT, SOT, SSL")
    c2.metric("Resubmissions This Week", resubmissions_this_week, latest_week.strftime("Week of %b %d"))
    c3.metric("Open ESB Items", open_failures, "Need resubmit or root-cause")
    c4.metric("Outstanding Recon Items", bank_outstanding, latest_bank_week.strftime("Week ending %b %d"))

    tabs = st.tabs([
        "Bank Reconciliation (Sunsystem / Genelco / Capsil -> VEFT)",
        "ESB Failures & Resubmissions to SUN GL",
        "Genelco -> SUN GL Oversight",
        "IFRS17 Interface (ESB to SUN GL)",
    ])

    with tabs[0]:
        st.subheader("Provides general support to the bank reconciliation area")
        st.write("Monitoring Sunsystem, Genelco, and Capsil transactions against the VEFT bank file with control logs and outstanding items.")

        trend_fig = px.line(
            bank_df,
            x="week",
            y="match_pct",
            color="system",
            markers=True,
            title="Match % to VEFT by Week",
            labels={"week": "Week", "match_pct": "Match %", "system": "System"},
        )
        trend_fig.update_traces(line_width=3)
        st.plotly_chart(trend_fig, use_container_width=True)

        latest_outstanding = bank_df[bank_df["week"] == latest_bank_week][["system", "outstanding", "note"]]
        bar_fig = px.bar(
            latest_outstanding,
            x="system",
            y="outstanding",
            text="outstanding",
            title=f"Outstanding Items vs VEFT (Week of {latest_bank_week.strftime('%b %d')})",
            labels={"system": "System", "outstanding": "Outstanding Items"},
        )
        bar_fig.update_traces(textposition="outside")
        st.plotly_chart(bar_fig, use_container_width=True)

        st.write("Control log highlights")
        st.dataframe(
            bank_df.sort_values(["week", "system"], ascending=[False, True]).reset_index(drop=True),
            use_container_width=True,
        )

    with tabs[1]:
        st.subheader("Monitors and re-submits ESB failures to SUN GL (BEL, CAB, SLA, SLB, SLT, SOT, SSL)")
        st.write("Daily ESB interfaces from Capsil and GIAS with resubmission tracking and control logs for Finance weekly reporting.")

        latest_summary = (
            esb_df[esb_df["week"] == latest_week]
            .groupby("feed")[["failed", "resubmitted", "open"]]
            .sum()
            .reset_index()
        )
        melted = latest_summary.melt(id_vars="feed", var_name="status", value_name="count")
        resub_fig = px.bar(
            melted,
            x="feed",
            y="count",
            color="status",
            barmode="group",
            text="count",
            title=f"Resubmission Posture by Feed (Week of {latest_week.strftime('%b %d')})",
            labels={"feed": "Feed", "count": "Items"},
        )
        resub_fig.update_traces(textposition="outside")
        st.plotly_chart(resub_fig, use_container_width=True)

        open_trend = (
            esb_df.groupby("week")[["failed", "resubmitted", "open"]].sum().reset_index()
        )
        open_fig = px.line(
            open_trend,
            x="week",
            y=["failed", "resubmitted", "open"],
            markers=True,
            title="Failures, Resubmissions, and Open Items by Week",
            labels={"week": "Week", "value": "Count", "variable": "Status"},
        )
        open_fig.update_traces(line_width=3)
        st.plotly_chart(open_fig, use_container_width=True)

        st.write("Control log (weekly)")
        st.dataframe(
            esb_df.sort_values(["week", "feed"]).reset_index(drop=True),
            use_container_width=True,
        )

    with tabs[2]:
        st.subheader("Oversight of Genelco -> SUN GL interface (weekly/monthly)")
        st.write("Maintains control logs and produces weekly/monthly status reports for Finance leadership.")

        genelco_fig = px.line(
            genelco_df,
            x="week",
            y="success_rate",
            markers=True,
            title="Genelco -> SUN GL Success Rate",
            labels={"week": "Week", "success_rate": "Success %"},
        )
        genelco_fig.update_traces(line_width=3)
        st.plotly_chart(genelco_fig, use_container_width=True)

        st.write("Weekly / Monthly control log snapshot")
        st.dataframe(
            genelco_df.sort_values("week", ascending=False).reset_index(drop=True),
            use_container_width=True,
        )

    with tabs[3]:
        st.subheader("IFRS17 postings from ESB to SUN GL")
        st.write("Interface status for IFRS17 transactions with posting percentages and notes for Finance.")

        recent_ifrs = ifrs_df.sort_values("date", ascending=False)
        ifrs_fig = px.bar(
            recent_ifrs,
            x="date",
            y="posting_pct",
            text="posting_pct",
            title="Posting % to SUN GL per IFRS17 batch",
            labels={"date": "Date", "posting_pct": "Posting %"},
        )
        ifrs_fig.update_traces(textposition="outside")
        st.plotly_chart(ifrs_fig, use_container_width=True)

        st.write("Batch log")
        st.dataframe(recent_ifrs, use_container_width=True)
