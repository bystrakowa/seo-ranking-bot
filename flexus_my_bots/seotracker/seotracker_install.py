import asyncio
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_my_bots.seotracker import seotracker_bot
from flexus_my_bots.seotracker import seotracker_prompts

TOOL_NAMESET = {t.name for t in seotracker_bot.TOOLS}

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=seotracker_prompts.main_prompt,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(
            TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT
        ),
        fexp_nature="NATURE_SEMI_AUTONOMOUS",
        fexp_inactivity_timeout=3600,
        fexp_description=(
            "Runs SEO position checks on request: fetches Google Search Console data for your domain, "
            "checks competitor positions, computes deltas vs previous runs, and generates an XLSX report."
        ),
    )),
]


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=seotracker_bot.SEOTRACKER_ROOTDIR,
        marketable_accent_color="#1A73E8",
        marketable_title1="SEO Ranking Tracker",
        marketable_title2="Track your Google positions, monitor competitors, download XLSX reports.",
        marketable_author="Flexus",
        marketable_occupation="SEO Analyst",
        marketable_description=(seotracker_bot.SEOTRACKER_ROOTDIR / "README.md").read_text(),
        marketable_typical_group="Marketing",
        marketable_setup_default=seotracker_bot.SEOTRACKER_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Run SEO check", "feat_expert": "default", "feat_depends_on_setup": ["GscServiceAccountJson"]},
            {"feat_question": "Show my ranking history", "feat_expert": "default", "feat_depends_on_setup": ["GscServiceAccountJson"]},
        ],
        marketable_intro_message=(
            "Hi! I'm your SEO Ranking Tracker. I can check your Google search positions "
            "for your tracked keywords, compare them with competitors, and deliver a full XLSX report. "
            "Just say \"Run SEO check\" to get started!"
        ),
        marketable_preferred_model_expensive="gpt-5.4",
        marketable_preferred_model_cheap="gpt-5.4-mini",
        marketable_experts=[(name, exp.filter_tools(seotracker_bot.TOOLS)) for name, exp in EXPERTS],
        add_integrations_into_expert_system_prompt=seotracker_bot.SEOTRACKER_INTEGRATIONS,
        marketable_schedule=[],
        marketable_tags=["SEO", "Marketing", "Analytics", "Google"],
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("seotracker_install")
    asyncio.run(install(client))
