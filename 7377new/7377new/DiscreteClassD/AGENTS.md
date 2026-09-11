{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 This is a 24 V discrete BTL Class-D audio amplifier.\
\
Engineering decisions are made by the user and ChatGPT.\
Do not substitute components or alter circuit topology without being asked.\
\
Target switching frequency: approximately 400 kHz.\
\
Power stage:\
- UCC27301ADRCR gate drivers\
- DMN6070SY MOSFETs\
- stereo: four half bridges, two per BTL channel\
- Both OPA1656 packages use +12V_GD; VREF is 2.5 V and logic/comparators use +5V_A\
\
Important:\
- Never swap datasheet pin numbers.\
- Confirm pin mappings against supplied datasheets.\
- Do not suppress ERC errors automatically.\
- Keep custom symbols and footprints in project-local libraries.\
- Before large schematic changes, preserve the existing file.\
- Run kicad-cli schematic ERC after modifications.\
- Export a PDF after significant schematic changes.}