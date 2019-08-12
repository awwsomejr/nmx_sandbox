#!/usr/bin/perl
##Author: Basil Morrison 
#######################
use DBI;
use Text::CSV_XS qw( csv );
#use Utilities;
use Excel::Writer::XLSX;
use Data::Dumper;
use List::Util qw( max );
use Net::SSH::Expect;
use Net::SCP::Expect;


my @freq_mask_token;
my @freq_mask;
my @out_str_id;
my @frequency;
my @region_id;
my @orig;

my $dbhost = "172.16.168.95";
my $dbport = "3306";
my $dbuser = "dsops";
my $dbpass = "!MyGeNeRiC1!";

`/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/cleanup_err.pl`;
`/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/cleanup_shuff.pl`;

open LI_OUTFILE, ">>/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/LI/shuff.sql";
open LI_ERR, ">>/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/prod_scripts/li_err.csv";
open LIPK_OUTFILE, ">>/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/LIPK/shuff.sql";
open NJ_OUTFILE, ">>/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/NJ/shuff.sql";
open NJ_ERR, ">>/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/prod_scripts/nj_err.csv";
open NJPK_OUTFILE, ">>/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/NJPK/shuff.sql";

print LI_ERR "SSR,Outstream-ID,Frequency,Region-ID\n";
print NJ_ERR "SSR,Outstream-ID,Frequency,Region-ID\n";

while (<>) {
       chomp $_;

       @split=split (/\|/, $_, 8);
#       print Dumper @split;

       my $ssr = "$split[0]";
       my $out_str_id = "$split[1]";
       my $new_out_stream = "$split[2]";
       my $old_freq = "$split[3]";
       my $new_freq = "$split[4]";
       my $cur_region_id = "$split[5]";
       my $new_region_id = "$split[6]";
       my $diff_region_id = "$split[7]";

       my $pad_old_freq = sprintf( "%d0000", $old_freq );
       my $pad_new_freq = sprintf( "%d0000", $new_freq );

          chomp $ssr;
          chomp $out_str_id;
          chomp $new_out_stream;
          chomp $old_freq;
          chomp $new_freq;
          chomp $cur_region_id;
          chomp $new_region_id;
          chomp $diff_region_id;
          chomp $pad_old_freq;
          chomp $pad_new_freq;

#       $ssr = $ssrGlob;

if ( grep( /[a-zA-Z]/, $cur_region_id ) ) {
  print "\n";
  print "invalid region ID(s): $cur_region_id\n";
  print "Verify input data and try again..\n";
  print "\n";
  exit;
}
if ( grep( /[a-zA-Z]/, $new_region_id ) ) {
  print "\n";
  print "invalid region ID(s): $cur_region_id\n";
  print "Verify input data and try again..\n";
  print "\n";
  exit;
}


my @all_uniqueness;
my @uniqueness;
my @new_uniqueness;
my @old_footprintMask;


 my $dsn1 = "dbi:mysql:dbname=$ssr;host=$dbhost;port=$dbport;";
 my $dbh1 = DBI->connect($dsn1, $dbuser, $dbpass) or die "Connection error: $DBI::errstr";

#used for to get all uniquenesses
my $sthx=$dbh1->prepare("SELECT COUNT(DELIVERY_NUM) FROM $ssr.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = $out_str_id AND FOOTPRINT_MASK <> 0");
   $sthx->execute();
#get all uniqueness (will be used to create new uniqueness)
##
while (my $cnt = $sthx->fetchrow_hashref()) {
    $count = $cnt->{"COUNT(DELIVERY_NUM)"};
    # print "count = $count\n";

    if ($count == 0) {
        print "\n";
        print "Outstream ID \"$out_str_id\" missing from CafeDev database. Please check input file / verify databse is updated.\n";
        print "\n";
#        $dbh1->disconnect();
        exit;
  }
}
#check if db is empty
#######################################################
my $dsn = "dbi:mysql:dbname=$ssr;host=$dbhost;port=$dbport;";
my $dbh = DBI->connect($dsn, $dbuser, $dbpass) or die "Connection error: $DBI::errstr";

#used for to get all uniquenesses
my $sth2=$dbh->prepare("SELECT DELIVERY_NUM FROM $ssr.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = $out_str_id AND FOOTPRINT_MASK <> 0");
   $sth2->execute();

#get all uniqueness (will be used to create new uniqueness)
##
while (my $ref5 = $sth2->fetchrow_hashref()) {
     push @all_uniqueness, "$ref5->{DELIVERY_NUM}\n";
     chomp @all_uniqueness;
        }
my @sorted = sort @all_uniqueness;
my $highest = $sorted[0];
my $new_uniqueness = $highest + 1;
$dbh->disconnect();
print "\n";
print "new uniqueness: $new_uniqueness\n";
###############################################
my $dsn2 = "dbi:mysql:dbname=$ssr;host=$dbhost;port=$dbport;";
my $dbh2 = DBI->connect($dsn, $dbuser, $dbpass) or die "Connection error: $DBI::errstr";
#used to get old uniqueness
my $sthx=$dbh2->prepare("SELECT DELIVERY_NUM FROM $ssr.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = $out_str_id AND FREQUENCY = $pad_old_freq AND FOOTPRINT_MASK <> 0");
   $sthx->execute();
#get old uniquness
##
while (my $ref2 = $sthx->fetchrow_hashref()) {
      push @uniqueness, "$ref2->{DELIVERY_NUM}\n";
      chomp @uniqueness;
        }
$dbh2->disconnect();
my $uniqueness = shift @uniqueness;
print "current uniqueness: $uniqueness\n";
###############################################
my $dsn3 = "dbi:mysql:dbname=$ssr;host=$dbhost;port=$dbport;";
my $dbh3 = DBI->connect($dsn3, $dbuser, $dbpass) or die "Connection error: $DBI::errstr";

my $sth3=$dbh3->prepare("SELECT FOOTPRINT_MASK FROM $ssr.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = $out_str_id AND FREQUENCY = $pad_old_freq AND FOOTPRINT_MASK <> 0");
   $sth3->execute();
#get old footprint mask
##
while (my $ref3 = $sth3->fetchrow_hashref()) {
     push @old_footprintMask, "$ref3->{FOOTPRINT_MASK}\n";
     chomp @old_footprintMask;
     }
$dbh3->disconnect();
my $old_footprintMask = shift @old_footprintMask;
print "old footprint mask: $old_footprintMask\n";
###############################################
my $dsn4 = "dbi:mysql:dbname=$ssr;host=$dbhost;port=$dbport;";
my $dbh4 = DBI->connect($dsn4, $dbuser, $dbpass) or die "Connection error: $DBI::errstr";
#get new footprint mask
##
my @new_footprintMask;

#$binary= create_bin($cur_region_id);
$binary= create_bin($new_region_id);

$sth4=$dbh4->prepare("SELECT CONV(REVERSE(\"$binary\"), 2, 10) as FM");
   $sth4->execute();

   while (my $ref4 = $sth4->fetchrow_hashref()) {
     push @new_footprintMask, $ref4->{FM};
     chomp @new_footprintMask;
     }
$dbh4->disconnect();
my $new_footprintMask = shift @new_footprintMask;
print "new footprint mask: $new_footprintMask\n";
################################################
my $dsn5 = "dbi:mysql:dbname=$ssr;host=$dbhost;port=$dbport;";
my $dbh5 = DBI->connect($dsn5, $dbuser, $dbpass) or die "Connection error: $DBI::errstr";
#get diff_footprintmask (this is the last field of piped input file)
##
my @diff_footprintMask;

$binary2= create_bin($diff_region_id);

$sth6=$dbh5->prepare("SELECT CONV(REVERSE(\"$binary2\"), 2, 10) as FM");
   $sth6->execute();

   while (my $ref6 = $sth6->fetchrow_hashref()) {
     push @diff_footprintMask, $ref6->{FM};
     chomp @diff_footprintMask;
     }
$dbh5->disconnect();
my $diff_footprintMask = shift @diff_footprintMask;
print "diff footprint mask: $diff_footprintMask\n";
#####################################################
sub create_bin {
  my $std = shift;
  my @spl = split(",", $std);
  my @bin ;
  for (my $i = 0;$i <= max @spl;$i++){
     if (grep{/^$i$/} @spl){
       $bin[$i] = "1";
      }else{
       $bin[$i] = "0";
     }
   }
 return join("", @bin);
}

##update current uniqueness with new footprint mask
##

###############################################################################################################################################################################################################
#for Legacy SSRS LI & NJ
#If frequency or transport did not exist prior
#INSERT SSR.OUT_STREAM_DELIVERY (<fields>) VALUES (<fields prior>, OUT_STREAM_ID=$out_str_id, FREQUENCY=$pad_old_freq, DELIVERY_NUM = $uniqueness WHERE OUT_STREAM_ID =  $out_str_id and DELIVERY_NUM=$out_str_id, <fields post>);\n"
#If exited
#UPDATE SSR.OUT_STREAM_DELIVERY SET OUT_STREAM_ID=$out_str_id, FREQUENCY=$pad_old_freq  WHERE OUT_STREAM_ID =  $out_str_id and DELIVERY_NUM=$new_uniqueness;\n"
my $dsn7 = "dbi:mysql:dbname=$ssr;host=$dbhost;port=$dbport;";
my $dbh7 = DBI->connect($dsn7, $dbuser, $dbpass) or die "Connection error: $DBI::errstr";
   $sth7=$dbh7->prepare("SELECT COUNT(*) FROM $ssr.OUT_STREAM_DELIVERY WHERE OUT_STREAM_ID = $out_str_id OR FREQUENCY = $pad_old_freq");
   $sth7->execute();
      my $ref7 = $sth7->fetchrow_hashref();
      my $exists = "$ref7->{'COUNT(*)'}";
      print "LI & NJ freq/outstream count: $exists\n";
      print "\n";
      undef $exists;
#   $dbh7->disconnect();

########-LI
    if ( $ssr eq 'SSR_LI' ) {
     if (($uniqueness ne '') || ($old_footprintMask ne '')) {
       if ($exists = 0) {
            print LI_OUTFILE "INSERT INTO SSR.OUT_STREAM_DELIVERY (OUT_STREAM_ID, SI_OUT_STREAM_ID, DELIVERY_NUM, DELIVERY_TYPE, REGION_ID, FOOTPRINT_MASK, FREQUENCY, FEC_OUTER, MODULATION, SYMBOL_RATE, FEC_INNER, ORBIT_POSITION, WEST_EAST_FLAG, POLARISATION, BANDWIDTH, CONSTELLATION, HIERARCHY, CODE_RATE_HP, CODE_RATE_LP, GUARD_INTERVAL, TRANSMISSION_MODE, OTHER_FREQUENCY, NOTES, SCTE_TX_SYSTEM, SCTE_SPLIT_MODE, ROLL_OFF, PLP_ID, T2_SYSTEM_ID, SISO_MISO_FLAG) VALUES ('$out_str_id', '-1', '$new_uniqueness', '5', '0', '$diff_footprintMask', '$pad_new_freq', '0', '16', '5360537', '3', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '', '2', '0', '0', '0', '0', '0');\n";
        }
        else {
            print LI_OUTFILE "UPDATE SSR.OUT_STREAM_DELIVERY SET FREQUENCY=$pad_old_freq, DELIVERY_NUM = $uniqueness WHERE OUT_STREAM_ID =  $out_str_id;\n";
            }
       }
        else {
           print LI_ERR "$ssr,$out_str_id,$old_freq,$cur_region_id\n";
    }
  }

########-LIPK
     if ( $ssr eq 'SSR_LIPK' ) {
            print LIPK_OUTFILE "UPDATE SSR.OUT_STREAM_DELIVERY SET FOOTPRINT_MASK = $new_footprintMask, FREQUENCY=$pad_old_freq, DELIVERY_NUM = $uniqueness WHERE FOOTPRINT_MASK = $old_footprintMask AND OUT_STREAM_ID =  $out_str_id;\n";
            print LIPK_OUTFILE "commit;\n";
            print LIPK_OUTFILE "INSERT INTO SSR.OUT_STREAM_DELIVERY (OUT_STREAM_ID, SI_OUT_STREAM_ID, DELIVERY_NUM, DELIVERY_TYPE, REGION_ID, FOOTPRINT_MASK, FREQUENCY, FEC_OUTER, MODULATION, SYMBOL_RATE, FEC_INNER, ORBIT_POSITION, WEST_EAST_FLAG, POLARISATION, BANDWIDTH, CONSTELLATION, HIERARCHY, CODE_RATE_HP, CODE_RATE_LP, GUARD_INTERVAL, TRANSMISSION_MODE, OTHER_FREQUENCY, NOTES, SCTE_TX_SYSTEM, SCTE_SPLIT_MODE, ROLL_OFF, PLP_ID, T2_SYSTEM_ID, SISO_MISO_FLAG) VALUES ('$out_str_id', '-1', '$new_uniqueness', '5', null, '$diff_footprintMask', '$pad_new_freq', null, '16', '5360537', '3', null, null, null, null, null, null, null, null, null, null, null, null, '2', '0', '0', null, null, null);\n";
            }

########-NJ
    if ( $ssr eq 'SSR_NJ' ) {
     if (($uniqueness ne '') || ($old_footprintMask ne '')) {
       if ($exists = 0) {
            print NJ_OUTFILE "INSERT INTO SSR.OUT_STREAM_DELIVERY (OUT_STREAM_ID, SI_OUT_STREAM_ID, DELIVERY_NUM, DELIVERY_TYPE, REGION_ID, FOOTPRINT_MASK, FREQUENCY, FEC_OUTER, MODULATION, SYMBOL_RATE, FEC_INNER, ORBIT_POSITION, WEST_EAST_FLAG, POLARISATION, BANDWIDTH, CONSTELLATION, HIERARCHY, CODE_RATE_HP, CODE_RATE_LP, GUARD_INTERVAL, TRANSMISSION_MODE, OTHER_FREQUENCY, NOTES, SCTE_TX_SYSTEM, SCTE_SPLIT_MODE, ROLL_OFF, PLP_ID, T2_SYSTEM_ID, SISO_MISO_FLAG) VALUES ('$out_str_id', '-1', '$new_uniqueness', '5', '0', '$diff_footprintMask', '$pad_new_freq', '0', '16', '5360537', '3', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '', '2', '0', '0', '0', '0', '0');\n";
        }
        else {
            print NJ_OUTFILE "UPDATE SSR.OUT_STREAM_DELIVERY SET FREQUENCY=$pad_old_freq, DELIVERY_NUM = $uniqueness WHERE OUT_STREAM_ID =  $out_str_id;\n";
            }
       }
        else {
           print NJ_ERR "$ssr,$out_str_id,$old_freq,$cur_region_id\n";
    }
  }

#######-NJPK
     if ( $ssr eq 'SSR_NJPK' ) {
           print NJPK_OUTFILE "UPDATE SSR.OUT_STREAM_DELIVERY SET FOOTPRINT_MASK = $new_footprintmask, FREQUENCY=$pad_old_freq, DELIVERY_NUM = $uniqueness WHERE FOOTPRINT_MASK = $old_footprintMask AND OUT_STREAM_ID =  $out_str_id;\n";
           print NJPK_OUTFILE "INSERT INTO SSR.OUT_STREAM_DELIVERY (OUT_STREAM_ID, SI_OUT_STREAM_ID, DELIVERY_NUM, DELIVERY_TYPE, REGION_ID, FOOTPRINT_MASK, FREQUENCY, FEC_OUTER, MODULATION, SYMBOL_RATE, FEC_INNER, ORBIT_POSITION, WEST_EAST_FLAG, POLARISATION, BANDWIDTH, CONSTELLATION, HIERARCHY, CODE_RATE_HP, CODE_RATE_LP, GUARD_INTERVAL, TRANSMISSION_MODE, OTHER_FREQUENCY, NOTES, SCTE_TX_SYSTEM, SCTE_SPLIT_MODE, ROLL_OFF, PLP_ID, T2_SYSTEM_ID, SISO_MISO_FLAG) VALUES ('$out_str_id', '-1', '$new_uniqueness', '5', '0', '$diff_footprintMask', '$pad_new_freq', '0', '16', '5360537', '3', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '', '2', '0', '0', '0', '0', '0');\n";
            }

    }
undef $new_uniqueness;
undef $uniqueness;
undef $new_footprintMask;
undef $out_str_id;
undef $diff_footprintMask;
undef $pad_new_freq;
undef $old_footprintMask;
undef $diff_footprintMask;
undef $pad_new_freq;
undef $pad_old_freq;
#print LI_OUTFILE "UPDATE SSR.OUT_STREAM_DELIVERY SET OUT_STREAM_ID=$out_str_id, xxxFOOTPRINT_MASK = $new_footprintMaskxxx, FREQUENCY=$pad_old_freq, DELIVERY_NUM = $uniqueness WHERE xxxxFOOTPRINT_MASK = $old_footprintMaskxxxx AND OUT_STREAM_ID =  $out_str_id;\n";


close (LI_OUTFILE);
close (LIPK_OUTFILE);
close (NJ_OUTFILE);
close (NJPK_OUTFILE);

if (!(-z "/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/LI/shuff.sql")) {
`/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/plsql_li.pl`;

        stopSecondary ('10.248.118.40');
        stopPrimary ('10.248.118.39');
        prepSsr('10.248.118.39');
        startup ('10.248.118.39');
        startup ('10.248.118.40');

    }

if (!(-z "/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/LIPK/shuff.sql")) {
`/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/plsql_lipk.pl`;

        stopSecondary ('10.248.118.81');
        stopPrimary ('10.248.118.80');
        prepSsr('10.248.118.80');
        startup ('10.248.118.80');
        startup ('10.248.118.81');

    }

if (!(-z "/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/NJ/shuff.sql")) {
`/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/plsql_nj.pl`;

        stopSecondary ('10.250.99.31');
        stopPrimary ('10.250.99.30');
        prepSsr('10.250.99.30');
        startup ('10.250.99.30');
        startup ('10.250.99.31');

    }

if (!(-z "/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/NJPK/shuff.sql")) {
`/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/plsql_njpk.pl`;

        stopSecondary ('10.250.99.76');
        stopPrimary ('10.250.99.75');
        prepSsr('10.250.99.75');
        startup ('10.250.99.75');
        startup ('10.250.99.76');

    }


sub stopPrimary {

         my $host = shift;

            my $ssh = Net::SSH::Expect->new (
              host      => "$host",
              password  => 'get2know',
              user      => 'root',
              raw_pty   => 1,
              timeout => 3
            );
            my $login_output = $ssh->login();
               $ssh->exec("cd /var/log/nds/usg");
               $ssh->exec("nds_service nds_dsrv_usg stop");
               $ssh->exec("nds_service nds_usg stop");

              verifyStop($host);
              print "nds_dsrv_usg is stopped...\n";
              $ssh->close();
          }

sub stopSecondary {

         my $host = shift;

            my $ssh = Net::SSH::Expect->new (
              host      => "$host",
              password  => 'get2know',
              user      => 'root',
              raw_pty   => 1,
              timeout => 3
            );
            my $login_output = $ssh->login();
               $ssh->exec("cd /var/log/nds/usg");
               $ssh->exec("nds_service nds_dsrv_usg stop");
               $ssh->exec("nds_service nds_usg stop");

              verifyStop($host);
              print "nds_dsrv_usg is stopped...\n";
              $ssh->close();
          }



   sub prepSsr {
          my $host = shift;
          $counter = 0;
          $ssh = Net::SSH::Expect->new (
                 host      => "$host",
                 password  => 'get2know',
                 user      => 'root',
                 raw_pty   => 1,
                 timeout   => 3
                );
                my $login_output = $ssh->login();
                while (copySql($host) =~ /[a-z]/) {
                        if ($counter >=3) {
                                print "There is a problem with scp on SSR $host.\n";
                                break;
                        }
                        sleep(10);
                        $counter++;
                }
              $ssh->exec(". /opt/oracle/SSR.env");
              $ssh->exec("cd /home/ndsuser/scripts");
              my $dispDb = $ssh->exec("sqlplus -L -s system/systemssr\@SSR \@shuffle.sql");
              print "$dispDb\n";
              #$counter++;

             $ssh->close();
      }


   sub copySql {

   my $host = shift;
   my $region;

   if ($host eq "10.248.118.80" || $host eq "10.248.118.81") {
       $region = 'LIPK';
     }
   if ($host eq "10.248.118.39" || $host eq "10.248.118.40") {
       $region = 'LI';
     }
   if ($host eq "10.250.99.30" || $host eq "10.280.99.31") {
       $region = 'NJ';
     }
   if ($host eq "10.250.99.75" || $host eq "10.250.99.76") {
       $region = 'NJPK';
     }

            my $scpe = Net::SCP::Expect->new;
               $scpe->login('root', 'get2know');
              eval { $scpe->scp("/home/dncs/halo/SCRIPTS/SANDBOX/shuffle/$region/shuffle.sql","$host:/home/ndsuser/scripts/");};

              return $@;
        }

sub startup {

     my $host = shift;

          my $ssh = Net::SSH::Expect->new (
              host      => "$host",
              password  => 'get2know',
              user      => 'root',
              raw_pty   => 1,
              timeout => 3
            );
              my $login_output = $ssh->login();
              $ssh->exec("nds_service nds_dsrv_usg start");
              $ssh->exec("nds_service nds_usg start");

              verifyStart($host);
              print "nds_dsrv_usg is started...\n";
              $ssh->close();
          }

#sqlplus -L -s system/systemssr@LIPKUSSR @shuffle.sql
#LIPKUSSR
#LIUSSR
#NJUSSR
#NJPKUSSR

sub verifyStop {

          my $host = shift;

          #get_latest_log($host);
          $counter = 0;
          while (check_state_of_proc($host, 'nds_dsrv_usg') !~ /NOT/){
              if ($counter >=20) {
                  print "There seems to be a problem with the nds_dsrv_usg service. Please check SSR and run the shuffle script again.\n";
                  exit;
                }
               sleep(10);
               $counter++;
               #get_latest_log($host);
            }
           $counter = 0;
           while (check_state_of_proc($host, 'nds_usg') !~ /NOT/){
              if ($counter >=20) {
                  print "There seems to be a problem with the nds_usg service. Please check SSR and run the shuffle script again.\n";
                  exit;
                }
               sleep(10);
               $counter++;
               #get_latest_log($host);
            }

          }

sub verifyStart {

        my $host = shift;

        #get_latest_log($host);
        $counter = 0;
        while (check_state_of_proc($host, 'nds_dsrv_usg') =~ /NOT/){
              if ($counter >=20) {
                  print "There seems to be a problem with the dsrv service. Please check SSR and run the shuffle script again.\n";
                  exit;
                }
               sleep(10);
               $counter++;
               #get_latest_log($host);
            }
              $counter = 0;
              while (check_state_of_proc($host, 'nds_usg') =~ /NOT/){
              if ($counter >=20) {
                  print "There seems to be a problem with the dsrv service. Please check SSR and run the shuffle script again.\n";
                  exit;
                }
               sleep(10);
               $counter++;
               #get_latest_log($host);
            }
}


sub check_state_of_proc {
        my $host = shift;
        my $proc = shift;
        my $ssh = Net::SSH::Expect->new (
              host      => $host,
              password  => 'get2know',
              user      => 'root',
              raw_pty   => 1,
              timeout => 3
       );
       my $resp = "$proc is NOT running";
       my $login_output = $ssh->login();
       my @result = $ssh->exec("nds_service");
       foreach (@result) {
                if (/$proc/) {
                        if (!/NOT/){
                           $resp = "$proc is running";
                        }
                }
        }
        return $resp;
}
=cut
sub #get_latest_log{
     my $host = shift;
     my $scpe = Net::SCP::Expect->new;
     $scpe->login('root', 'get2know');
     $scpe->scp("/tmp/$host/usg/slave","$host:/var/log/nds/usg");
    }

sub check_state_of_proc {
    my $host    = shift;
    my $process = shift;
    my $state;
    open FH, "<", "/tmp/$host/usg/slave" or die $!;
    while (<FH>) {
        if (/$process/i){
           if (/running/){
                $state = 'running';
        }elsif (/NOT/){
                $state = 'NOT';
        }
      }
    close FH;
    return $state;
    }

=cut
