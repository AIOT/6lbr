/*
 * Copyright (c) 2010, Swedish Institute of Computer Science.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * $Id: project-conf.h,v 1.1 2010/11/03 15:46:41 adamdunkels Exp $
 */

#ifndef __PROJECT_RPL_WEB_CONF_H__
#define __PROJECT_RPL_WEB_CONF_H__

#if !UIP_CONF_IPV6_RPL
#undef UIP_CONF_ROUTER
#define UIP_CONF_ROUTER            0
#endif

#undef QUEUEBUF_CONF_NUM
#define QUEUEBUF_CONF_NUM          5

#undef UIP_CONF_BUFFER_SIZE
#define UIP_CONF_BUFFER_SIZE    260

#undef UIP_CONF_RECEIVE_WINDOW
#define UIP_CONF_RECEIVE_WINDOW  60

#undef WEBSERVER_CONF_CFS_CONNS
#define WEBSERVER_CONF_CFS_CONNS 2

/* Reserve space for a file name (default is to not use file name) */
#undef WEBSERVER_CONF_CFS_PATHLEN
#define WEBSERVER_CONF_CFS_PATHLEN 80

//Temporary : When RDC is enabled the mote can not communicate with Econotag
#undef NETSTACK_CONF_MAC
#define NETSTACK_CONF_MAC     		csma_driver

#undef NETSTACK_CONF_RDC
#define NETSTACK_CONF_RDC     		nullrdc_driver

#if CETIC_6LBR_DISABLE_ACK
//Disable  802.15.4 ACK
#undef NULLRDC_CONF_802154_AUTOACK
#define NULLRDC_CONF_802154_AUTOACK	0
#undef NULLRDC_CONF_802154_AUTOACK_HW
#define NULLRDC_CONF_802154_AUTOACK_HW	0
#else
#undef NULLRDC_CONF_802154_AUTOACK
#define NULLRDC_CONF_802154_AUTOACK	1
#endif

#undef SKY_CONF_MAX_TX_POWER
#define SKY_CONF_MAX_TX_POWER 	31


/* RPL & Neighbor Info */

#define RPL_MAX_DAG_PER_INSTANCE	2
#define RPL_MAX_INSTANCES		1
#define RPL_CONF_MAX_PARENTS_PER_DAG	24
#define NEIGHBOR_CONF_MAX_NEIGHBORS	24

#undef UIP_CONF_DS6_NBR_NBU
#define UIP_CONF_DS6_NBR_NBU     24

#undef UIP_CONF_DS6_ROUTE_NBU
#define UIP_CONF_DS6_ROUTE_NBU   24

#endif /* __PROJECT_RPL_WEB_CONF_H__ */
