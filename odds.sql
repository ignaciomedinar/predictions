with odds as (
    select wo.League,
        t.espn_teams as local,
        t2.espn_teams as visitor,
        wo.date,
        wo.Bookmaker,
        wo.HomeOdds,
        wo.DrawOdds,
        wo.AwayOdds,
        ROW_NUMBER () over (
            partition by t.espn_teams,
            t2.espn_teams
            order by wo.HomeOdds desc
        ) as home_rank,
        ROW_NUMBER () over (
            partition by t.espn_teams,
            t2.espn_teams
            order by wo.DrawOdds desc
        ) as draw_rank,
        ROW_NUMBER () over (
            partition by t.espn_teams,
            t2.espn_teams
            order by wo.AwayOdds desc
        ) as away_rank
    from weekly_odds wo
        left join teams t on t.odds_teams = wo.Home
        left join teams t2 on t2.odds_teams = wo.Away
    where t.espn_teams is not NULL
        and t2.espn_teams is not null
),
top_odds as (
    SELECT distinct o.league,
        o.local,
        o.visitor,
        o.date,
        -- Top bookmaker and odds for home
        home.bookmaker AS top_HomeBookmaker,
        home.HomeOdds AS top_HomeOdds,
        -- Top bookmaker and odds for draw
        draw.bookmaker AS top_DrawBookmaker,
        draw.drawOdds AS top_DrawOdds,
        -- Top bookmaker and odds for away
        away.bookmaker AS top_AwayBookmaker,
        away.awayOdds AS top_AwayOdds
    FROM odds o
        LEFT JOIN odds home ON o.league = home.league
        AND o.local = home.local
        AND o.visitor = home.visitor
        AND o.date = home.date
        AND home.home_rank = 1
        LEFT JOIN odds draw ON o.league = draw.league
        AND o.local = draw.local
        AND o.visitor = draw.visitor
        AND o.date = draw.date
        AND draw.draw_rank = 1
        LEFT JOIN odds away ON o.league = away.league
        AND o.local = away.local
        AND o.visitor = away.visitor
        AND o.date = away.date
        AND away.away_rank = 1
)
select distinct p.*,
    od.top_HomeBookmaker,
    od.top_HomeOdds,
    od.top_DrawBookmaker,
    od.top_DrawOdds,
    od.top_AwayBookmaker,
    od.top_AwayOdds
from predictions_espn p
    left join top_odds od on p.local = od.local
    and p.Visitor = od.visitor