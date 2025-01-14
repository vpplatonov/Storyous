USE [story_api_local]
GO
/****** Object:  Schema [storyous]    Script Date: 7/7/2024 5:29:06 PM ******/
CREATE SCHEMA [storyous]
GO
/****** Object:  Table [storyous].[address_parts]    Script Date: 7/7/2024 5:29:06 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[address_parts](
	[place_id] [varchar](150) NOT NULL,
	[street] [nvarchar](150) NULL,
	[street_number] [varchar](150) NULL,
	[city] [nvarchar](150) NULL,
	[country] [nvarchar](150) NULL,
	[country_code] [varchar](10) NULL,
	[zip] [varchar](50) NULL,
	[latitude] [decimal](12, 8) NULL,
	[longitude] [decimal](12, 8) NULL,
 CONSTRAINT [PK_address_parts] PRIMARY KEY CLUSTERED 
(
	[place_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[bills]    Script Date: 7/7/2024 5:29:06 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[bills](
	[bill_id] [varchar](150) NOT NULL,
	[place_id] [varchar](150) NOT NULL,
	[session_created] [datetime] NULL,
	[created_at] [datetime] NULL,
	[paid_at] [datetime] NULL,
	[fiscalized_at] [datetime] NULL,
	[final_price] [money] NULL,
	[final_price_without_tax] [money] NULL,
	[tax_summaries] [varchar](400) NULL,
	[discount] [numeric](10, 4) NULL,
	[rounding] [numeric](10, 4) NULL,
	[tips] [money] NULL,
	[currency_code] [varchar](10) NULL,
	[refunded] [bit] NULL,
	[payment_method] [varchar](50) NULL,
	[created_by] [int] NULL,
	[paid_by] [int] NULL,
	[person_count] [int] NOT NULL,
	[desk_id] [varchar](50) NULL,
	[issued_as_vat_payer] [bit] NULL,
	[customer_id] [varchar](150) NULL,
	[last_modified_at] [datetime] NULL,
 CONSTRAINT [PK_bills] PRIMARY KEY CLUSTERED 
(
	[bill_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[clients_and_auth]    Script Date: 7/7/2024 5:29:06 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[clients_and_auth](
	[client_id] [varchar](150) NOT NULL,
	[secret] [varchar](150) NULL,
	[client_name] [nvarchar](150) NULL,
	[token_type] [varchar](50) NULL,
	[access_token] [varchar](2000) NULL,
	[expires_at] [datetime] NULL,
 CONSTRAINT [PK_clients_and_auth] PRIMARY KEY CLUSTERED 
(
	[client_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[fiscal_data]    Script Date: 7/7/2024 5:29:06 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[fiscal_data](
	[bill_id] [varchar](150) NOT NULL,
	[pid] [int] IDENTITY(1,1) NOT NULL,
	[mode] [int] NULL,
	[endpoint] [varchar](150) NULL,
	[fik] [varchar](150) NULL,
	[pkp] [varchar](400) NULL,
	[bkp] [varchar](150) NULL,
	[http_status_code] [varchar](10) NULL,
 CONSTRAINT [PK_fiscal_data] PRIMARY KEY CLUSTERED 
(
	[pid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[invoice_data]    Script Date: 7/7/2024 5:29:06 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[invoice_data](
	[bill_id] [varchar](150) NOT NULL,
	[pid] [int] IDENTITY(1,1) NOT NULL,
	[data] [nvarchar](max) NULL,
 CONSTRAINT [PK_invoice_data] PRIMARY KEY CLUSTERED 
(
	[pid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [storyous].[items]    Script Date: 7/7/2024 5:29:06 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[items](
	[bill_id] [varchar](150) NOT NULL,
	[pid] [int] IDENTITY(1,1) NOT NULL,
	[name] [nvarchar](150) NULL,
	[amount] [numeric](18, 6) NULL,
	[measure] [varchar](50) NULL,
	[price] [money] NULL,
	[vat_rate] [numeric](10, 4) NULL,
	[product_id] [varchar](150) NULL,
	[decoded_id] [int] NULL,
	[category_id] [varchar](150) NULL,
	[has_additions_with_code] [varchar](150) NULL,
	[additions_code] [varchar](150) NULL,
	[ean] [varchar](50) NULL,
 CONSTRAINT [PK_items] PRIMARY KEY CLUSTERED 
(
	[pid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[merchants]    Script Date: 7/7/2024 5:29:06 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[merchants](
	[client_id] [varchar](150) NOT NULL,
	[merchant_id] [varchar](150) NOT NULL,
	[name] [nvarchar](150) NULL,
	[business_id] [varchar](50) NULL,
	[vat_id] [varchar](50) NULL,
	[is_vat_payer] [bit] NULL,
	[country_code] [varchar](10) NULL,
	[currency_code] [varchar](10) NULL,
 CONSTRAINT [PK_merchants] PRIMARY KEY CLUSTERED 
(
	[merchant_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[order_provider]    Script Date: 7/7/2024 5:29:06 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[order_provider](
	[bill_id] [varchar](150) NOT NULL,
	[pid] [int] IDENTITY(1,1) NOT NULL,
	[code] [varchar](50) NULL,
	[order_id] [varchar](150) NULL,
 CONSTRAINT [PK_order_provider] PRIMARY KEY CLUSTERED 
(
	[pid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[payments]    Script Date: 7/7/2024 5:29:07 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[payments](
	[bill_id] [varchar](150) NOT NULL,
	[pid] [int] IDENTITY(1,1) NOT NULL,
	[payment_method] [varchar](50) NULL,
	[price_with_vat] [money] NULL,
 CONSTRAINT [PK_payments] PRIMARY KEY CLUSTERED 
(
	[pid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[person]    Script Date: 7/7/2024 5:29:07 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[person](
	[person_id] [int] NOT NULL,
	[full_name] [nvarchar](150) NULL,
	[user_name] [nvarchar](50) NULL,
 CONSTRAINT [PK_person] PRIMARY KEY CLUSTERED 
(
	[person_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[places]    Script Date: 7/7/2024 5:29:07 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[places](
	[merchant_id] [varchar](150) NOT NULL,
	[place_id] [varchar](150) NOT NULL,
	[name] [nvarchar](150) NULL,
	[state] [varchar](50) NULL,
 CONSTRAINT [PK_places] PRIMARY KEY CLUSTERED 
(
	[place_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [storyous].[taxes]    Script Date: 7/7/2024 5:29:07 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [storyous].[taxes](
	[bill_id] [varchar](150) NOT NULL,
	[pid] [int] IDENTITY(1,1) NOT NULL,
	[vat] [numeric](10, 4) NULL,
	[total_vat] [money] NULL,
	[total_without_vat] [money] NULL,
 CONSTRAINT [PK_taxes] PRIMARY KEY CLUSTERED 
(
	[pid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_bills]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_bills] ON [storyous].[bills]
(
	[bill_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_bills_created_by]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_bills_created_by] ON [storyous].[bills]
(
	[created_by] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_bills_paid_by]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_bills_paid_by] ON [storyous].[bills]
(
	[paid_by] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_fiscal_data_bill]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_fiscal_data_bill] ON [storyous].[fiscal_data]
(
	[bill_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_invoice_data_bill]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_invoice_data_bill] ON [storyous].[invoice_data]
(
	[bill_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_items_bill]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_items_bill] ON [storyous].[items]
(
	[bill_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_client]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_client] ON [storyous].[merchants]
(
	[client_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_order_provider_bill]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_order_provider_bill] ON [storyous].[order_provider]
(
	[bill_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_merchant]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_merchant] ON [storyous].[places]
(
	[merchant_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_taxes_bill]    Script Date: 7/7/2024 5:29:07 PM ******/
CREATE NONCLUSTERED INDEX [IX_taxes_bill] ON [storyous].[taxes]
(
	[bill_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [storyous].[bills] ADD  CONSTRAINT [DF_bills_person_count]  DEFAULT ((1)) FOR [person_count]
GO
ALTER TABLE [storyous].[bills]  WITH CHECK ADD  CONSTRAINT [FK_bills_person] FOREIGN KEY([created_by])
REFERENCES [storyous].[person] ([person_id])
GO
ALTER TABLE [storyous].[bills] CHECK CONSTRAINT [FK_bills_person]
GO
ALTER TABLE [storyous].[bills]  WITH CHECK ADD  CONSTRAINT [FK_bills_person1] FOREIGN KEY([paid_by])
REFERENCES [storyous].[person] ([person_id])
GO
ALTER TABLE [storyous].[bills] CHECK CONSTRAINT [FK_bills_person1]
GO
ALTER TABLE [storyous].[bills]  WITH CHECK ADD  CONSTRAINT [FK_bills_places] FOREIGN KEY([place_id])
REFERENCES [storyous].[places] ([place_id])
GO
ALTER TABLE [storyous].[bills] CHECK CONSTRAINT [FK_bills_places]
GO
ALTER TABLE [storyous].[fiscal_data]  WITH CHECK ADD  CONSTRAINT [FK_fiscal_data_bills] FOREIGN KEY([bill_id])
REFERENCES [storyous].[bills] ([bill_id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [storyous].[fiscal_data] CHECK CONSTRAINT [FK_fiscal_data_bills]
GO
ALTER TABLE [storyous].[invoice_data]  WITH CHECK ADD  CONSTRAINT [FK_invoice_data_bills] FOREIGN KEY([bill_id])
REFERENCES [storyous].[bills] ([bill_id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [storyous].[invoice_data] CHECK CONSTRAINT [FK_invoice_data_bills]
GO
ALTER TABLE [storyous].[items]  WITH CHECK ADD  CONSTRAINT [FK_items_bills] FOREIGN KEY([bill_id])
REFERENCES [storyous].[bills] ([bill_id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [storyous].[items] CHECK CONSTRAINT [FK_items_bills]
GO
ALTER TABLE [storyous].[merchants]  WITH CHECK ADD  CONSTRAINT [FK_merchants_clients_and_auth] FOREIGN KEY([client_id])
REFERENCES [storyous].[clients_and_auth] ([client_id])
GO
ALTER TABLE [storyous].[merchants] CHECK CONSTRAINT [FK_merchants_clients_and_auth]
GO
ALTER TABLE [storyous].[order_provider]  WITH CHECK ADD  CONSTRAINT [FK_order_provider_bills] FOREIGN KEY([bill_id])
REFERENCES [storyous].[bills] ([bill_id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [storyous].[order_provider] CHECK CONSTRAINT [FK_order_provider_bills]
GO
ALTER TABLE [storyous].[payments]  WITH CHECK ADD  CONSTRAINT [FK_payments_bills] FOREIGN KEY([bill_id])
REFERENCES [storyous].[bills] ([bill_id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [storyous].[payments] CHECK CONSTRAINT [FK_payments_bills]
GO
ALTER TABLE [storyous].[places]  WITH NOCHECK ADD  CONSTRAINT [FK_places_address_parts] FOREIGN KEY([place_id])
REFERENCES [storyous].[address_parts] ([place_id])
ON UPDATE CASCADE
ON DELETE CASCADE
NOT FOR REPLICATION 
GO
ALTER TABLE [storyous].[places] NOCHECK CONSTRAINT [FK_places_address_parts]
GO
ALTER TABLE [storyous].[places]  WITH CHECK ADD  CONSTRAINT [FK_places_merchants] FOREIGN KEY([merchant_id])
REFERENCES [storyous].[merchants] ([merchant_id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [storyous].[places] CHECK CONSTRAINT [FK_places_merchants]
GO
ALTER TABLE [storyous].[taxes]  WITH CHECK ADD  CONSTRAINT [FK_taxes_bills] FOREIGN KEY([bill_id])
REFERENCES [storyous].[bills] ([bill_id])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [storyous].[taxes] CHECK CONSTRAINT [FK_taxes_bills]
GO
