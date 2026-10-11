# Session 18 — Final Project

The end-of-course build. Each numbered folder is one project. Open that folder's README first.

| Folder | Project |
|---|---|
| [01_AI_Talking_Avatar](./01_AI_Talking_Avatar/) | Airport guide that listens, retrieves, and speaks. Show students the [expected demo](./01_AI_Talking_Avatar/expected_demo/) first. |
| [02_Newspaper_Digitizer](./02_Newspaper_Digitizer/) | 1954 newspaper. PaddleOCR finds the boxes. A small decision model picks the previous box and groups each article. English and Tamil. |
| [03_Apex_Counter](./03_Apex_Counter/) | Modernize a parts desk: **ASP.NET Web Forms on .NET Framework 4.0** → **Blazor Server on .NET 8** |
| [04_Intelligent_Document_Processing](./04_Intelligent_Document_Processing/) | Upload English, Tamil, Arabic, or a bilingual page. Click one value and only that box lights up |

For Apex Counter, the legacy Web Forms app is in the folder. Students run it as ground truth, convert a **copy** with AWS Transform to Blazor Server on .NET 8, then run three agents: ground truth, evaluate, and repair. The original Web Forms project stays. The target UI is Blazor Server, not MVC, Razor Pages, or React.

← [Course README](../README.md) · [S17 Decision Models](../17_Decision_Models/)
